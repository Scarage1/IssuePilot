"""
Integration Tests for IssuePilot API
"""

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.schemas import GitHubIssue, AnalysisResult


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self):
        """Test health endpoint returns ok"""
        with patch("app.main.GitHubClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.check_rate_limit = AsyncMock(return_value={"remaining": 100})
            mock_client.return_value = mock_instance

            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "version" in data
            assert "dependencies" in data
            assert "cache_size" in data


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "IssuePilot"
        assert "version" in data
        assert "docs" in data


class TestAnalyzeEndpoint:
    """Tests for analyze endpoint"""

    def test_analyze_invalid_repo_format(self):
        """Test analyze with invalid repo format"""
        response = client.post(
            "/analyze", json={"repo": "invalid-format", "issue_number": 123}
        )
        assert response.status_code == 422  # Validation error

    def test_analyze_missing_issue_number(self):
        """Test analyze without issue number"""
        response = client.post("/analyze", json={"repo": "owner/repo"})
        assert response.status_code == 422

    def test_analyze_negative_issue_number(self):
        """Test analyze with negative issue number"""
        response = client.post(
            "/analyze", json={"repo": "owner/repo", "issue_number": -1}
        )
        assert response.status_code == 422

    @patch("app.main.GitHubClient")
    @patch("app.main.AIEngine")
    @patch("app.main.DuplicateFinder")
    def test_analyze_success(self, mock_duplicate, mock_ai, mock_github):
        """Test successful analysis"""
        # Mock GitHub client
        mock_issue = GitHubIssue(
            number=123,
            title="Test Issue",
            body="Test body",
            state="open",
            labels=["bug"],
            url="https://github.com/owner/repo/issues/123",
            comments=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
        )
        mock_github_instance = MagicMock()
        mock_github_instance.get_issue = AsyncMock(return_value=mock_issue)
        mock_github_instance.get_open_issues = AsyncMock(return_value=[])
        mock_github.return_value = mock_github_instance

        # Mock AI engine
        mock_analysis = AnalysisResult(
            summary="Test summary",
            root_cause="Test root cause",
            solution_steps=["Step 1"],
            checklist=["Item 1"],
            labels=["bug"],
            similar_issues=[],
        )
        mock_ai_instance = MagicMock()
        mock_ai_instance.analyze_issue = AsyncMock(return_value=mock_analysis)
        mock_ai.return_value = mock_ai_instance

        # Mock duplicate finder
        mock_duplicate_instance = MagicMock()
        mock_duplicate_instance.find_similar_issues = AsyncMock(return_value=[])
        mock_duplicate.return_value = mock_duplicate_instance

        response = client.post(
            "/analyze", json={"repo": "owner/repo", "issue_number": 123}
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "root_cause" in data
        assert "solution_steps" in data
        assert "checklist" in data
        assert "labels" in data


class TestExportEndpoint:
    """Tests for export endpoint"""

    def test_export_success(self):
        """Test successful markdown export"""
        analysis = {
            "summary": "Test summary",
            "root_cause": "Test root cause",
            "solution_steps": ["Step 1", "Step 2"],
            "checklist": ["Item 1", "Item 2"],
            "labels": ["bug"],
            "similar_issues": [],
        }

        response = client.post("/export", json={"analysis": analysis})

        assert response.status_code == 200
        data = response.json()
        assert "markdown" in data
        assert "Test summary" in data["markdown"]
        assert "Step 1" in data["markdown"]

    def test_export_invalid_request(self):
        """Test export with invalid request"""
        response = client.post("/export", json={})
        assert response.status_code == 422


class TestRateLimitEndpoint:
    """Tests for rate limit endpoint"""

    @patch("app.main.GitHubClient")
    def test_rate_limit_success(self, mock_github):
        """Test successful rate limit check"""
        mock_github_instance = MagicMock()
        mock_github_instance.check_rate_limit = AsyncMock(
            return_value={"limit": 5000, "remaining": 4999, "reset_at": 1699999999}
        )
        mock_github.return_value = mock_github_instance

        response = client.get("/rate-limit")

        assert response.status_code == 200
        data = response.json()
        assert "limit" in data
        assert "remaining" in data


class TestBatchAnalyzeEndpoint:
    """Tests for batch analyze endpoint"""

    def test_batch_analyze_invalid_repo_format(self):
        """Test batch analyze with invalid repo format"""
        response = client.post(
            "/analyze/batch", json={"repo": "invalid-format", "issue_numbers": [123]}
        )
        assert response.status_code == 422

    def test_batch_analyze_empty_issue_numbers(self):
        """Test batch analyze with empty issue numbers list"""
        response = client.post(
            "/analyze/batch", json={"repo": "owner/repo", "issue_numbers": []}
        )
        assert response.status_code == 422

    def test_batch_analyze_too_many_issues(self):
        """Test batch analyze with more than 10 issues"""
        response = client.post(
            "/analyze/batch",
            json={"repo": "owner/repo", "issue_numbers": list(range(1, 15))},
        )
        assert response.status_code == 422

    @patch("app.main.GitHubClient")
    @patch("app.main.AIEngine")
    @patch("app.main.DuplicateFinder")
    def test_batch_analyze_success(self, mock_duplicate, mock_ai, mock_github):
        """Test successful batch analysis"""

        # Create mock issues
        def create_mock_issue(number):
            return GitHubIssue(
                number=number,
                title=f"Test Issue {number}",
                body=f"Test body {number}",
                state="open",
                labels=["bug"],
                url=f"https://github.com/owner/repo/issues/{number}",
                comments=[],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
            )

        mock_github_instance = MagicMock()
        mock_github_instance.get_issue = AsyncMock(
            side_effect=lambda repo, num: create_mock_issue(num)
        )
        mock_github_instance.get_open_issues = AsyncMock(return_value=[])
        mock_github.return_value = mock_github_instance

        # Mock AI engine
        mock_analysis = AnalysisResult(
            summary="Test summary",
            root_cause="Test root cause",
            solution_steps=["Step 1"],
            checklist=["Item 1"],
            labels=["bug"],
            similar_issues=[],
        )
        mock_ai_instance = MagicMock()
        mock_ai_instance.analyze_issue = AsyncMock(return_value=mock_analysis)
        mock_ai.return_value = mock_ai_instance

        # Mock duplicate finder
        mock_duplicate_instance = MagicMock()
        mock_duplicate_instance.find_similar_issues = AsyncMock(return_value=[])
        mock_duplicate.return_value = mock_duplicate_instance

        response = client.post(
            "/analyze/batch", json={"repo": "owner/repo", "issue_numbers": [1, 2, 3]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["repo"] == "owner/repo"
        assert data["total"] == 3
        assert data["successful"] == 3
        assert data["failed"] == 0
        assert len(data["results"]) == 3
        for result in data["results"]:
            assert result["success"] is True
            assert result["result"] is not None

    @patch("app.main.GitHubClient")
    @patch("app.main.AIEngine")
    @patch("app.main.DuplicateFinder")
    def test_batch_analyze_partial_failure(self, mock_duplicate, mock_ai, mock_github):
        """Test batch analysis with some issues failing"""
        # Clear cache to ensure clean test
        from app.main import analysis_cache

        analysis_cache.clear()

        # Mock GitHub client - issue 2 not found
        def get_issue_side_effect(repo, number):
            if number == 2:
                raise Exception("404 Not Found")
            return GitHubIssue(
                number=number,
                title=f"Test Issue {number}",
                body=f"Test body {number}",
                state="open",
                labels=["bug"],
                url=f"https://github.com/owner/repo/issues/{number}",
                comments=[],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
            )

        mock_github_instance = MagicMock()
        mock_github_instance.get_issue = AsyncMock(side_effect=get_issue_side_effect)
        mock_github_instance.get_open_issues = AsyncMock(return_value=[])
        mock_github.return_value = mock_github_instance

        # Mock AI engine
        mock_analysis = AnalysisResult(
            summary="Test summary",
            root_cause="Test root cause",
            solution_steps=["Step 1"],
            checklist=["Item 1"],
            labels=["bug"],
            similar_issues=[],
        )
        mock_ai_instance = MagicMock()
        mock_ai_instance.analyze_issue = AsyncMock(return_value=mock_analysis)
        mock_ai.return_value = mock_ai_instance

        # Mock duplicate finder
        mock_duplicate_instance = MagicMock()
        mock_duplicate_instance.find_similar_issues = AsyncMock(return_value=[])
        mock_duplicate.return_value = mock_duplicate_instance

        response = client.post(
            "/analyze/batch", json={"repo": "owner/repo", "issue_numbers": [1, 2, 3]}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["successful"] == 2
        assert data["failed"] == 1

        # Check that issue 2 failed
        issue_2_result = next(r for r in data["results"] if r["issue_number"] == 2)
        assert issue_2_result["success"] is False
        assert "not found" in issue_2_result["error"].lower()
