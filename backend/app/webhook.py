"""
GitHub Webhook Handler for IssuePilot

Handles incoming GitHub webhook events for automatic issue analysis.
Supports issue opened, edited, and labeled events.
"""

import hashlib
import hmac
import logging
import os
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("issuepilot.webhook")

# Webhook secret for signature verification
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


class WebhookIssue(BaseModel):
    """GitHub issue data from webhook payload"""

    number: int
    title: str
    body: Optional[str] = ""
    state: str
    html_url: str
    labels: list = []

    @property
    def label_names(self) -> list[str]:
        """Extract label names from label objects"""
        return [
            label.get("name", "") for label in self.labels if isinstance(label, dict)
        ]


class WebhookRepository(BaseModel):
    """GitHub repository data from webhook payload"""

    full_name: str
    private: bool = False


class WebhookSender(BaseModel):
    """GitHub user who triggered the webhook"""

    login: str
    type: str = "User"


class IssueWebhookPayload(BaseModel):
    """Schema for GitHub issue webhook payload"""

    action: str = Field(
        ..., description="The action that was performed (opened, edited, labeled, etc.)"
    )
    issue: WebhookIssue
    repository: WebhookRepository
    sender: WebhookSender


class WebhookResponse(BaseModel):
    """Response schema for webhook endpoint"""

    status: str
    message: str
    action: Optional[str] = None
    repo: Optional[str] = None
    issue_number: Optional[int] = None
    analysis_triggered: bool = False


class WebhookConfig(BaseModel):
    """Webhook configuration"""

    enabled: bool
    auto_analyze_on_open: bool = True
    auto_analyze_on_edit: bool = False
    auto_analyze_on_label: bool = False
    required_label: Optional[str] = None  # Only analyze if this label is present
    excluded_labels: list[str] = []  # Don't analyze if any of these labels are present


def get_webhook_config() -> WebhookConfig:
    """Get webhook configuration from environment"""
    return WebhookConfig(
        enabled=bool(WEBHOOK_SECRET),
        auto_analyze_on_open=os.getenv("WEBHOOK_AUTO_ANALYZE_OPEN", "true").lower()
        == "true",
        auto_analyze_on_edit=os.getenv("WEBHOOK_AUTO_ANALYZE_EDIT", "false").lower()
        == "true",
        auto_analyze_on_label=os.getenv("WEBHOOK_AUTO_ANALYZE_LABEL", "false").lower()
        == "true",
        required_label=os.getenv("WEBHOOK_REQUIRED_LABEL"),
        excluded_labels=(
            os.getenv("WEBHOOK_EXCLUDED_LABELS", "").split(",")
            if os.getenv("WEBHOOK_EXCLUDED_LABELS")
            else []
        ),
    )


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256.

    Args:
        payload: Raw request body bytes
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    if not WEBHOOK_SECRET:
        logger.warning(
            "Webhook secret not configured - skipping signature verification"
        )
        return True  # Allow in development if no secret configured

    if not signature:
        logger.warning("No signature provided in webhook request")
        return False

    # GitHub sends signature as "sha256=<hash>"
    if signature.startswith("sha256="):
        signature = signature[7:]

    # Calculate expected signature
    expected = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature)


def should_analyze_issue(
    payload: IssueWebhookPayload, config: WebhookConfig
) -> tuple[bool, str]:
    """
    Determine if an issue should be analyzed based on the webhook event.

    Args:
        payload: Webhook payload
        config: Webhook configuration

    Returns:
        Tuple of (should_analyze, reason)
    """
    issue = payload.issue
    action = payload.action

    # Check if action triggers analysis
    if action == "opened" and not config.auto_analyze_on_open:
        return False, "Auto-analyze on open is disabled"

    if action == "edited" and not config.auto_analyze_on_edit:
        return False, "Auto-analyze on edit is disabled"

    if action == "labeled" and not config.auto_analyze_on_label:
        return False, "Auto-analyze on label is disabled"

    # Only process specific actions
    if action not in ("opened", "edited", "labeled"):
        return False, f"Action '{action}' does not trigger analysis"

    # Check for required label
    if config.required_label:
        if config.required_label not in issue.label_names:
            return False, f"Required label '{config.required_label}' not present"

    # Check for excluded labels
    for excluded in config.excluded_labels:
        if excluded and excluded in issue.label_names:
            return False, f"Excluded label '{excluded}' is present"

    # Skip closed issues
    if issue.state != "open":
        return False, "Issue is not open"

    return True, f"Analysis triggered by {action} event"


def format_webhook_log(payload: IssueWebhookPayload) -> str:
    """Format webhook payload for logging"""
    return (
        f"[{payload.action}] {payload.repository.full_name}#{payload.issue.number} "
        f"'{payload.issue.title[:50]}...' by @{payload.sender.login}"
    )
