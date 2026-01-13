"""
Tests for GitHub Client
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.github_client import GitHubClient
from app.schemas import GitHubIssue


class TestGitHubClient:
    """Tests for GitHubClient class"""

    def test_init_without_token(self):
        """Test initialization without token"""
        with patch.dict('os.environ', {}, clear=True):
            client = GitHubClient()
            assert client.token is None
            assert "Authorization" not in client.headers

    def test_init_with_token(self):
        """Test initialization with token"""
        client = GitHubClient(token="test_token")
        assert client.token == "test_token"
        assert client.headers["Authorization"] == "token test_token"

    @pytest.mark.asyncio
    async def test_get_issue_success(self):
        """Test successful issue fetch"""
        mock_issue_data = {
            "number": 123,
            "title": "Test Issue",
            "body": "Test body content",
            "state": "open",
            "labels": [{"name": "bug"}],
            "html_url": "https://github.com/owner/repo/issues/123",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        }
        
        mock_comments = []
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_issue_data
            mock_response.raise_for_status = MagicMock()
            
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance
            
            client = GitHubClient()
            
            # Mock get_issue_comments
            with patch.object(client, 'get_issue_comments', return_value=mock_comments):
                issue = await client.get_issue("owner/repo", 123)
        
            assert issue.number == 123
            assert issue.title == "Test Issue"
            assert issue.state == "open"

    @pytest.mark.asyncio
    async def test_get_issue_comments(self):
        """Test fetching issue comments"""
        mock_comments_data = [
            {"body": "First comment"},
            {"body": "Second comment"}
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_comments_data
            mock_response.raise_for_status = MagicMock()
            
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance
            
            client = GitHubClient()
            comments = await client.get_issue_comments("owner/repo", 123)
        
        assert len(comments) == 2
        assert comments[0] == "First comment"
        assert comments[1] == "Second comment"


class TestParseRepo:
    """Tests for repository parsing"""
    
    def test_valid_repo(self):
        """Test parsing valid repository string"""
        from app.utils import parse_repo
        
        owner, repo = parse_repo("facebook/react")
        assert owner == "facebook"
        assert repo == "react"
    
    def test_invalid_repo(self):
        """Test parsing invalid repository string"""
        from app.utils import parse_repo
        
        with pytest.raises(ValueError):
            parse_repo("invalid-format")
    
    def test_repo_with_special_chars(self):
        """Test parsing repo with allowed special characters"""
        from app.utils import parse_repo
        
        owner, repo = parse_repo("owner-name/repo.name")
        assert owner == "owner-name"
        assert repo == "repo.name"
