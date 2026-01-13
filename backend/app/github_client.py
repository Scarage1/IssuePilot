"""
GitHub API Client for IssuePilot
"""
import os
import httpx
from typing import Optional, List, Dict, Any
from .schemas import GitHubIssue
from .utils import parse_repo, sanitize_input


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client
        
        Args:
            token: GitHub personal access token (optional)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "IssuePilot/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
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
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
        
        # Fetch comments
        comments = await self.get_issue_comments(repo, issue_number)
        
        return GitHubIssue(
            number=data["number"],
            title=sanitize_input(data["title"]),
            body=sanitize_input(data.get("body") or ""),
            state=data["state"],
            labels=[label["name"] for label in data.get("labels", [])],
            url=data["html_url"],
            comments=comments,
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    async def get_issue_comments(
        self, 
        repo: str, 
        issue_number: int, 
        max_comments: int = 5
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
        url = f"{self.BASE_URL}/repos/{owner}/{repo_name}/issues/{issue_number}/comments"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, 
                headers=self.headers,
                params={"per_page": max_comments}
            )
            response.raise_for_status()
            data = response.json()
        
        return [sanitize_input(comment["body"]) for comment in data]
    
    async def get_open_issues(
        self, 
        repo: str, 
        max_issues: int = 100
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
        
        async with httpx.AsyncClient() as client:
            while len(all_issues) < max_issues:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params={
                        "state": "open",
                        "per_page": per_page,
                        "page": page
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                # Filter out pull requests
                issues = [
                    {
                        "number": issue["number"],
                        "title": sanitize_input(issue["title"]),
                        "body": sanitize_input(issue.get("body") or ""),
                        "url": issue["html_url"]
                    }
                    for issue in data
                    if "pull_request" not in issue
                ]
                
                all_issues.extend(issues)
                page += 1
                
                if len(data) < per_page:
                    break
        
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
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
        
        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data.get("description"),
            "language": data.get("language"),
            "topics": data.get("topics", []),
            "open_issues_count": data["open_issues_count"],
            "url": data["html_url"]
        }
    
    async def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check current GitHub API rate limit status
        
        Returns:
            Rate limit information
        """
        url = f"{self.BASE_URL}/rate_limit"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
        
        return {
            "limit": data["rate"]["limit"],
            "remaining": data["rate"]["remaining"],
            "reset_at": data["rate"]["reset"]
        }
