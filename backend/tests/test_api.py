"""
Integration Tests for IssuePilot API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.schemas import GitHubIssue, AnalysisResult


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns ok"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


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
            "/analyze",
            json={"repo": "invalid-format", "issue_number": 123}
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_missing_issue_number(self):
        """Test analyze without issue number"""
        response = client.post(
            "/analyze",
            json={"repo": "owner/repo"}
        )
        assert response.status_code == 422
    
    def test_analyze_negative_issue_number(self):
        """Test analyze with negative issue number"""
        response = client.post(
            "/analyze",
            json={"repo": "owner/repo", "issue_number": -1}
        )
        assert response.status_code == 422

    @patch('app.main.GitHubClient')
    @patch('app.main.AIEngine')
    @patch('app.main.DuplicateFinder')
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
            updated_at="2024-01-02T00:00:00Z"
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
            similar_issues=[]
        )
        mock_ai_instance = MagicMock()
        mock_ai_instance.analyze_issue = AsyncMock(return_value=mock_analysis)
        mock_ai.return_value = mock_ai_instance
        
        # Mock duplicate finder
        mock_duplicate_instance = MagicMock()
        mock_duplicate_instance.find_similar_issues = AsyncMock(return_value=[])
        mock_duplicate.return_value = mock_duplicate_instance
        
        response = client.post(
            "/analyze",
            json={"repo": "owner/repo", "issue_number": 123}
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
            "similar_issues": []
        }
        
        response = client.post(
            "/export",
            json={"analysis": analysis}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "markdown" in data
        assert "Test summary" in data["markdown"]
        assert "Step 1" in data["markdown"]
    
    def test_export_invalid_request(self):
        """Test export with invalid request"""
        response = client.post(
            "/export",
            json={}
        )
        assert response.status_code == 422


class TestRateLimitEndpoint:
    """Tests for rate limit endpoint"""
    
    @patch('app.main.GitHubClient')
    def test_rate_limit_success(self, mock_github):
        """Test successful rate limit check"""
        mock_github_instance = MagicMock()
        mock_github_instance.check_rate_limit = AsyncMock(return_value={
            "limit": 5000,
            "remaining": 4999,
            "reset_at": 1699999999
        })
        mock_github.return_value = mock_github_instance
        
        response = client.get("/rate-limit")
        
        assert response.status_code == 200
        data = response.json()
        assert "limit" in data
        assert "remaining" in data
