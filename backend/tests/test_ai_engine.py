"""
Tests for AI Engine
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.ai_engine import AIEngine, APIKeyError, ModelError, VALID_MODELS
from app.schemas import GitHubIssue, AnalysisResult


class TestAIEngine:
    """Tests for AIEngine class"""

    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(APIKeyError, match="API key not configured"):
                AIEngine()

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345'}):
            engine = AIEngine()
            assert engine.api_key == "test_key_that_is_long_enough_12345"
            assert engine.model == "gpt-4o-mini"
    
    def test_init_with_invalid_model(self):
        """Test initialization with invalid model raises error"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345', 'MODEL': 'invalid-model'}):
            with pytest.raises(ModelError, match="Invalid model"):
                AIEngine()
    
    def test_init_with_valid_models(self):
        """Test initialization accepts all valid models"""
        for model in VALID_MODELS:
            with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345'}):
                engine = AIEngine(model=model)
                assert engine.model == model

    def test_build_prompt(self):
        """Test prompt building"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345'}):
            engine = AIEngine()
            
            issue = GitHubIssue(
                number=123,
                title="Test Issue Title",
                body="Test issue body content",
                state="open",
                labels=["bug"],
                url="https://github.com/owner/repo/issues/123",
                comments=["Comment 1", "Comment 2"],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z"
            )
            
            prompt = engine._build_prompt(issue)
            
            assert "Test Issue Title" in prompt
            assert "Test issue body content" in prompt
            assert "Comment 1" in prompt

    def test_validate_result_with_valid_data(self):
        """Test result validation with valid data"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345'}):
            engine = AIEngine()
            
            result_data = {
                "summary": "Test summary",
                "root_cause": "Test root cause",
                "solution_steps": ["Step 1", "Step 2", "Step 3"],
                "checklist": ["Item 1", "Item 2", "Item 3"],
                "labels": ["bug", "enhancement"]
            }
            
            result = engine._validate_result(result_data)
            
            assert isinstance(result, AnalysisResult)
            assert result.summary == "Test summary"
            assert result.root_cause == "Test root cause"
            assert len(result.solution_steps) == 3
            assert len(result.checklist) == 3
            assert "bug" in result.labels

    def test_validate_result_with_missing_fields(self):
        """Test result validation fills in missing fields"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345'}):
            engine = AIEngine()
            
            result_data = {}
            
            result = engine._validate_result(result_data)
            
            assert isinstance(result, AnalysisResult)
            assert result.summary == "Unable to generate summary."
            assert len(result.solution_steps) > 0
            assert len(result.checklist) > 0
            assert "bug" in result.labels

    def test_validate_result_filters_invalid_labels(self):
        """Test that invalid labels are filtered out"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345'}):
            engine = AIEngine()
            
            result_data = {
                "summary": "Test",
                "root_cause": "Test",
                "solution_steps": ["Step 1"],
                "checklist": ["Item 1"],
                "labels": ["bug", "invalid-label", "feature", "random"]
            }
            
            result = engine._validate_result(result_data)
            
            assert "bug" in result.labels
            assert "feature" in result.labels
            assert "invalid-label" not in result.labels
            assert "random" not in result.labels

    @pytest.mark.asyncio
    async def test_analyze_issue(self):
        """Test full issue analysis"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"summary": "Test", "root_cause": "Test", "solution_steps": ["Step 1"], "checklist": ["Item 1"], "labels": ["bug"]}'))
        ]
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key_that_is_long_enough_12345'}):
            engine = AIEngine()
            engine.client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            issue = GitHubIssue(
                number=123,
                title="Test Issue",
                body="Test body",
                state="open",
                labels=[],
                url="https://github.com/owner/repo/issues/123",
                comments=[],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z"
            )
            
            result = await engine.analyze_issue(issue)
            
            assert isinstance(result, AnalysisResult)
            assert result.summary == "Test"
