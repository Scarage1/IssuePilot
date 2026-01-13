"""
Tests for GitHub webhook functionality
"""

import hashlib
import hmac
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.webhook import (
    verify_webhook_signature,
    should_analyze_issue,
    get_webhook_config,
    IssueWebhookPayload,
    WebhookConfig,
    WebhookIssue,
    WebhookRepository,
    WebhookSender,
    format_webhook_log,
)


class TestWebhookSignatureVerification:
    """Tests for webhook signature verification"""

    def test_verify_signature_with_valid_signature(self):
        """Test that valid signatures are accepted"""
        secret = "test-secret"
        payload = b'{"test": "data"}'

        # Calculate expected signature
        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        with patch("app.webhook.WEBHOOK_SECRET", secret):
            result = verify_webhook_signature(payload, f"sha256={expected}")
            assert result is True

    def test_verify_signature_with_invalid_signature(self):
        """Test that invalid signatures are rejected"""
        with patch("app.webhook.WEBHOOK_SECRET", "test-secret"):
            result = verify_webhook_signature(b'{"test": "data"}', "sha256=invalid")
            assert result is False

    def test_verify_signature_without_secret(self):
        """Test that missing secret allows all requests (dev mode)"""
        with patch("app.webhook.WEBHOOK_SECRET", ""):
            result = verify_webhook_signature(b'{"test": "data"}', "")
            assert result is True

    def test_verify_signature_without_signature_header(self):
        """Test that missing signature is rejected when secret is configured"""
        with patch("app.webhook.WEBHOOK_SECRET", "test-secret"):
            result = verify_webhook_signature(b'{"test": "data"}', "")
            assert result is False


class TestShouldAnalyzeIssue:
    """Tests for issue analysis decision logic"""

    @pytest.fixture
    def default_config(self):
        """Default webhook configuration"""
        return WebhookConfig(
            enabled=True,
            auto_analyze_on_open=True,
            auto_analyze_on_edit=False,
            auto_analyze_on_label=False,
            required_label=None,
            excluded_labels=[],
        )

    @pytest.fixture
    def sample_payload(self):
        """Sample webhook payload"""
        return IssueWebhookPayload(
            action="opened",
            issue=WebhookIssue(
                number=1,
                title="Test Issue",
                body="Test body",
                state="open",
                html_url="https://github.com/test/repo/issues/1",
                labels=[],
            ),
            repository=WebhookRepository(
                full_name="test/repo",
                private=False,
            ),
            sender=WebhookSender(
                login="testuser",
                type="User",
            ),
        )

    def test_analyze_on_open_enabled(self, default_config, sample_payload):
        """Test that opened issues trigger analysis when enabled"""
        sample_payload.action = "opened"
        should, reason = should_analyze_issue(sample_payload, default_config)
        assert should is True
        assert "opened" in reason

    def test_analyze_on_open_disabled(self, sample_payload):
        """Test that opened issues don't trigger analysis when disabled"""
        config = WebhookConfig(
            enabled=True,
            auto_analyze_on_open=False,
        )
        sample_payload.action = "opened"
        should, reason = should_analyze_issue(sample_payload, config)
        assert should is False

    def test_analyze_on_edit_enabled(self, sample_payload):
        """Test that edited issues trigger analysis when enabled"""
        config = WebhookConfig(
            enabled=True,
            auto_analyze_on_edit=True,
        )
        sample_payload.action = "edited"
        should, reason = should_analyze_issue(sample_payload, config)
        assert should is True

    def test_analyze_on_edit_disabled(self, default_config, sample_payload):
        """Test that edited issues don't trigger analysis when disabled"""
        sample_payload.action = "edited"
        should, reason = should_analyze_issue(sample_payload, default_config)
        assert should is False

    def test_analyze_on_label_enabled(self, sample_payload):
        """Test that labeled issues trigger analysis when enabled"""
        config = WebhookConfig(
            enabled=True,
            auto_analyze_on_label=True,
        )
        sample_payload.action = "labeled"
        should, reason = should_analyze_issue(sample_payload, config)
        assert should is True

    def test_unhandled_action_skipped(self, default_config, sample_payload):
        """Test that unhandled actions are skipped"""
        sample_payload.action = "closed"
        should, reason = should_analyze_issue(sample_payload, default_config)
        assert should is False
        assert "does not trigger" in reason

    def test_required_label_present(self, sample_payload):
        """Test that required label check passes when label is present"""
        config = WebhookConfig(
            enabled=True,
            auto_analyze_on_open=True,
            required_label="needs-analysis",
        )
        sample_payload.issue.labels = [{"name": "needs-analysis"}]
        should, reason = should_analyze_issue(sample_payload, config)
        assert should is True

    def test_required_label_missing(self, sample_payload):
        """Test that required label check fails when label is missing"""
        config = WebhookConfig(
            enabled=True,
            auto_analyze_on_open=True,
            required_label="needs-analysis",
        )
        sample_payload.issue.labels = []
        should, reason = should_analyze_issue(sample_payload, config)
        assert should is False
        assert "Required label" in reason

    def test_excluded_label_present(self, default_config, sample_payload):
        """Test that excluded labels prevent analysis"""
        default_config.excluded_labels = ["wontfix", "duplicate"]
        sample_payload.issue.labels = [{"name": "bug"}, {"name": "duplicate"}]
        should, reason = should_analyze_issue(sample_payload, default_config)
        assert should is False
        assert "Excluded label" in reason

    def test_closed_issue_skipped(self, default_config, sample_payload):
        """Test that closed issues are skipped"""
        sample_payload.issue.state = "closed"
        should, reason = should_analyze_issue(sample_payload, default_config)
        assert should is False
        assert "not open" in reason


class TestWebhookConfig:
    """Tests for webhook configuration"""

    def test_get_webhook_config_defaults(self):
        """Test default configuration values"""
        with patch.dict("os.environ", {}, clear=True):
            with patch("app.webhook.WEBHOOK_SECRET", ""):
                config = get_webhook_config()
                assert config.enabled is False
                assert config.auto_analyze_on_open is True
                assert config.auto_analyze_on_edit is False

    def test_get_webhook_config_with_secret(self):
        """Test configuration when secret is set"""
        with patch("app.webhook.WEBHOOK_SECRET", "test-secret"):
            config = get_webhook_config()
            assert config.enabled is True

    def test_get_webhook_config_custom_settings(self):
        """Test configuration with custom environment variables"""
        env = {
            "WEBHOOK_AUTO_ANALYZE_OPEN": "false",
            "WEBHOOK_AUTO_ANALYZE_EDIT": "true",
            "WEBHOOK_AUTO_ANALYZE_LABEL": "true",
            "WEBHOOK_REQUIRED_LABEL": "analyze-me",
            "WEBHOOK_EXCLUDED_LABELS": "spam,duplicate",
        }
        with patch.dict("os.environ", env):
            with patch("app.webhook.WEBHOOK_SECRET", "secret"):
                config = get_webhook_config()
                assert config.auto_analyze_on_open is False
                assert config.auto_analyze_on_edit is True
                assert config.auto_analyze_on_label is True
                assert config.required_label == "analyze-me"
                assert "spam" in config.excluded_labels
                assert "duplicate" in config.excluded_labels


class TestWebhookPayloadParsing:
    """Tests for webhook payload parsing"""

    def test_parse_issue_webhook_payload(self):
        """Test parsing a valid issue webhook payload"""
        payload_dict = {
            "action": "opened",
            "issue": {
                "number": 42,
                "title": "Test Issue Title",
                "body": "Issue description here",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/42",
                "labels": [
                    {"name": "bug"},
                    {"name": "help wanted"},
                ],
            },
            "repository": {
                "full_name": "owner/repo",
                "private": False,
            },
            "sender": {
                "login": "octocat",
                "type": "User",
            },
        }

        payload = IssueWebhookPayload(**payload_dict)

        assert payload.action == "opened"
        assert payload.issue.number == 42
        assert payload.issue.title == "Test Issue Title"
        assert payload.repository.full_name == "owner/repo"
        assert payload.sender.login == "octocat"
        assert payload.issue.label_names == ["bug", "help wanted"]

    def test_parse_minimal_payload(self):
        """Test parsing a minimal webhook payload"""
        payload_dict = {
            "action": "opened",
            "issue": {
                "number": 1,
                "title": "Test",
                "state": "open",
                "html_url": "https://github.com/test/repo/issues/1",
            },
            "repository": {
                "full_name": "test/repo",
            },
            "sender": {
                "login": "user",
            },
        }

        payload = IssueWebhookPayload(**payload_dict)
        assert payload.issue.body == ""
        assert payload.issue.labels == []


class TestFormatWebhookLog:
    """Tests for webhook log formatting"""

    def test_format_webhook_log(self):
        """Test log message formatting"""
        payload = IssueWebhookPayload(
            action="opened",
            issue=WebhookIssue(
                number=123,
                title="A very long issue title that should be truncated in logs",
                body="Body",
                state="open",
                html_url="https://github.com/test/repo/issues/123",
            ),
            repository=WebhookRepository(full_name="test/repo"),
            sender=WebhookSender(login="testuser"),
        )

        log_msg = format_webhook_log(payload)

        assert "[opened]" in log_msg
        assert "test/repo#123" in log_msg
        assert "@testuser" in log_msg
        assert "A very long issue" in log_msg


class TestWebhookEndpoint:
    """Integration tests for webhook endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from app.main import app

        return TestClient(app)

    def test_webhook_without_secret_returns_skipped(self, client):
        """Test that webhooks without secret configured return skipped"""
        with patch("app.webhook.WEBHOOK_SECRET", ""):
            with patch("app.main.get_webhook_config") as mock_config:
                mock_config.return_value = WebhookConfig(enabled=False)

                response = client.post(
                    "/webhook/github",
                    json={"action": "opened"},
                    headers={"X-GitHub-Event": "issues"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "skipped"
                assert "not configured" in data["message"]

    def test_webhook_config_endpoint(self, client):
        """Test webhook config endpoint returns configuration"""
        response = client.get("/webhook/config")

        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "auto_analyze_on_open" in data

    def test_webhook_ignores_non_issue_events(self, client):
        """Test that non-issue events are ignored"""
        with patch("app.webhook.WEBHOOK_SECRET", "test-secret"):
            with patch("app.main.get_webhook_config") as mock_config:
                mock_config.return_value = WebhookConfig(enabled=True)
                with patch("app.main.verify_webhook_signature", return_value=True):
                    response = client.post(
                        "/webhook/github",
                        json={"action": "push"},
                        headers={
                            "X-GitHub-Event": "push",
                            "X-Hub-Signature-256": "sha256=test",
                        },
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "ignored"
