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
    async def test_get_issue_not_found(self):
        """Test that a 404 error is raised for non-existent issues"""
        import httpx
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=mock_response
            )
            
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance
            
            client = GitHubClient()
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.get_issue("owner/repo", 99999)
    
    
    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """Test handling of network timeouts"""
        import httpx
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            # Simulate the network connection just hanging
            mock_instance.get.side_effect = httpx.ReadTimeout("Connection timed out")
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance
            
            client = GitHubClient()
            
            with pytest.raises(httpx.ReadTimeout):
                await client.get_issue("owner/repo", 1)  
    @pytest.mark.asyncio
    async def test_get_issue_with_missing_body(self):
        """Test get_issue when body is None"""
        mock_issue_data = {
            "number": 1,
            "title": "Issue without body",
            "body": None,
            "state": "open",
            "labels": [],
            "html_url": "https://github.com/o/r/issues/1",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

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

            with patch.object(client, "get_issue_comments", return_value=[]):
                issue = await client.get_issue("owner/repo", 1)

        assert issue.body == ""


    @pytest.mark.asyncio
    async def test_get_issue_with_no_labels(self):
        """Test get_issue when no labels exist"""
        mock_issue_data = {
            "number": 2,
            "title": "No labels issue",
            "body": "Test",
            "state": "open",
            "labels": [],
            "html_url": "url",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_issue_data
            mock_response.raise_for_status = MagicMock()

            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            client = GitHubClient()

            with patch.object(client, "get_issue_comments", return_value=[]):
                issue = await client.get_issue("owner/repo", 2)

        assert issue.labels == []


    @pytest.mark.asyncio
    async def test_get_issue_github_server_down(self):
        """
        Test behavior when GitHub server is unreachable (connection error).
        """
        import httpx

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx.ConnectError(
                "GitHub server unreachable"
            )
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            client = GitHubClient()

            with pytest.raises(httpx.ConnectError):
                await client.get_issue("owner/repo", 1)


    @pytest.mark.asyncio
    async def test_get_issue_comments_passes_limit_to_api(self):
        """
        Test that max_comments is correctly passed as per_page parameter
        to the GitHub API request.
        """
        mock_comments = [{"body": f"comment {i}"} for i in range(10)]

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_comments
            mock_response.raise_for_status = MagicMock()

            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            client = GitHubClient()
            comments = await client.get_issue_comments("owner/repo", 1, max_comments=5)

            # Assert API was called with correct per_page limit
            mock_instance.get.assert_called_once()
            _, kwargs = mock_instance.get.call_args
            assert kwargs["params"]["per_page"] == 5

        # Client returns whatever API returns (pagination handled by GitHub)
        assert len(comments) == 10


    @pytest.mark.asyncio
    async def test_get_open_issues_filters_pull_requests(self):
        """Test pull requests are excluded from open issues"""
        mock_data = [
            {"number": 1, "title": "Issue", "body": "", "html_url": "url"},
            {"number": 2, "title": "PR", "body": "", "html_url": "url", "pull_request": {}},
        ]

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status = MagicMock()

            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            client = GitHubClient()
            issues = await client.get_open_issues("owner/repo")

        assert len(issues) == 1
        assert issues[0]["number"] == 1


    @pytest.mark.asyncio
    async def test_check_rate_limit(self):
        """Test GitHub API rate limit parsing"""
        mock_rate_data = {
            "rate": {
                "limit": 5000,
                "remaining": 4999,
                "reset": 1700000000,
            }
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_rate_data
            mock_response.raise_for_status = MagicMock()

            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            client = GitHubClient()
            rate = await client.check_rate_limit()

        assert rate["limit"] == 5000
        assert rate["remaining"] == 4999

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
