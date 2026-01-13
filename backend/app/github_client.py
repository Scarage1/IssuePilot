"""
GitHub API Client for IssuePilot
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from .schemas import GitHubIssue
from .utils import parse_repo, sanitize_input

logger = logging.getLogger("issuepilot.github")

# Retry configuration
DEFAULT_MAX_RETRIES = int(os.getenv("GITHUB_MAX_RETRIES", "3"))
DEFAULT_BASE_DELAY = float(os.getenv("GITHUB_RETRY_DELAY", "1.0"))


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors"""
    pass


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub rate limit is exceeded"""
    pass


class GitHubNotFoundError(GitHubAPIError):
    """Raised when resource is not found"""
    pass


class GitHubClient:
    """Client for interacting with GitHub API"""

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY
    ):
        """
        Initialize GitHub client

        Args:
            token: GitHub personal access token (optional)
            max_retries: Maximum number of retry attempts for rate limit errors
            base_delay: Base delay in seconds for exponential backoff
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "IssuePilot/1.1",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            logger.debug("GitHub client initialized with token")
        else:
            logger.debug("GitHub client initialized without token (rate limits may apply)")

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry for rate limits.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for httpx
            
        Returns:
            httpx.Response
            
        Raises:
            GitHubRateLimitError: If rate limit exceeded after all retries
            GitHubNotFoundError: If resource not found
            GitHubAPIError: For other API errors
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method, url, headers=self.headers, **kwargs
                    )
                    
                    # Check for rate limit
                    if response.status_code == 403:
                        remaining = response.headers.get("X-RateLimit-Remaining", "0")
                        if remaining == "0":
                            reset_time = response.headers.get("X-RateLimit-Reset", "")
                            
                            if attempt < self.max_retries:
                                delay = self.base_delay * (2 ** attempt)
                                logger.warning(
                                    f"GitHub rate limit hit. Retry {attempt + 1}/{self.max_retries} "
                                    f"in {delay:.1f}s (reset: {reset_time})"
                                )
                                await asyncio.sleep(delay)
                                continue
                            else:
                                raise GitHubRateLimitError(
                                    f"GitHub API rate limit exceeded after {self.max_retries} retries. "
                                    f"Rate limit resets at timestamp: {reset_time}. "
                                    "Consider using a GitHub token for higher limits."
                                )
                    
                    # Check for 404
                    if response.status_code == 404:
                        raise GitHubNotFoundError(f"Resource not found: {url}")
                    
                    # Raise for other errors
                    response.raise_for_status()
                    return response
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise GitHubNotFoundError(f"Resource not found: {url}")
                last_exception = GitHubAPIError(f"GitHub API error: {str(e)}")
            except (GitHubRateLimitError, GitHubNotFoundError):
                raise
            except Exception as e:
                last_exception = GitHubAPIError(f"Request failed: {str(e)}")
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Request error, retry {attempt + 1}/{self.max_retries} in {delay:.1f}s: {e}")
                    await asyncio.sleep(delay)
        
        raise last_exception or GitHubAPIError("Request failed after all retries")

    async def get_issue(self, repo: str, issue_number: int) -> GitHubIssue:
        """
        Fetch issue details from GitHub

        Args:
            repo: Repository in format 'owner/repo'
            issue_number: Issue number

        Returns:
            GitHubIssue object with issue details
        """
        owner, repo_name = parse_repo(repo)
        url = f"{self.BASE_URL}/repos/{owner}/{repo_name}/issues/{issue_number}"
        
        logger.debug(f"Fetching issue: {repo}#{issue_number}")
        
        response = await self._request_with_retry("GET", url)
        data = response.json()

        # Fetch comments
        comments = await self.get_issue_comments(repo, issue_number)
        
        logger.debug(f"Issue fetched: {data['title'][:50]}...")

        return GitHubIssue(
            number=data["number"],
            title=sanitize_input(data["title"]),
            body=sanitize_input(data.get("body") or ""),
            state=data["state"],
            labels=[label["name"] for label in data.get("labels", [])],
            url=data["html_url"],
            comments=comments,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    async def get_issue_comments(
        self, repo: str, issue_number: int, max_comments: int = 5
    ) -> List[str]:
        """
        Fetch comments for an issue

        Args:
            repo: Repository in format 'owner/repo'
            issue_number: Issue number
            max_comments: Maximum number of comments to fetch

        Returns:
            List of comment body texts
        """
        owner, repo_name = parse_repo(repo)
        url = (
            f"{self.BASE_URL}/repos/{owner}/{repo_name}/issues/{issue_number}/comments"
        )

        response = await self._request_with_retry(
            "GET", url, params={"per_page": max_comments}
        )
        data = response.json()
        
        logger.debug(f"Fetched {len(data)} comments for {repo}#{issue_number}")

        return [sanitize_input(comment["body"]) for comment in data]

    async def get_open_issues(
        self, repo: str, max_issues: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch open issues from repository for duplicate detection

        Args:
            repo: Repository in format 'owner/repo'
            max_issues: Maximum number of issues to fetch

        Returns:
            List of issue dictionaries
        """
        owner, repo_name = parse_repo(repo)
        url = f"{self.BASE_URL}/repos/{owner}/{repo_name}/issues"

        all_issues = []
        page = 1
        per_page = min(100, max_issues)

        while len(all_issues) < max_issues:
            response = await self._request_with_retry(
                "GET",
                url,
                params={"state": "open", "per_page": per_page, "page": page}
            )
            data = response.json()

            if not data:
                break

            # Filter out pull requests
            issues = [
                {
                    "number": issue["number"],
                    "title": sanitize_input(issue["title"]),
                    "body": sanitize_input(issue.get("body") or ""),
                    "url": issue["html_url"],
                }
                for issue in data
                if "pull_request" not in issue
            ]

            all_issues.extend(issues)
            page += 1

            if len(data) < per_page:
                break
        
        logger.debug(f"Fetched {len(all_issues[:max_issues])} open issues from {repo}")

        return all_issues[:max_issues]

    async def get_repo_info(self, repo: str) -> Dict[str, Any]:
        """
        Fetch repository metadata

        Args:
            repo: Repository in format 'owner/repo'

        Returns:
            Repository metadata dictionary
        """
        owner, repo_name = parse_repo(repo)
        url = f"{self.BASE_URL}/repos/{owner}/{repo_name}"

        response = await self._request_with_retry("GET", url)
        data = response.json()

        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data.get("description"),
            "language": data.get("language"),
            "topics": data.get("topics", []),
            "open_issues_count": data["open_issues_count"],
            "url": data["html_url"],
        }

    async def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check current GitHub API rate limit status

        Returns:
            Rate limit information
        """
        url = f"{self.BASE_URL}/rate_limit"

        # Use direct request for rate limit check (no retry needed)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

        rate_info = {
            "limit": data["rate"]["limit"],
            "remaining": data["rate"]["remaining"],
            "reset_at": data["rate"]["reset"],
        }
        
        logger.debug(f"Rate limit: {rate_info['remaining']}/{rate_info['limit']}")
        
        return rate_info
