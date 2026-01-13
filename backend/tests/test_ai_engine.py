"""
Tests for AI Engine - OpenAI and Gemini Support
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.ai_engine import (
    AIEngine,
    APIKeyError,
    ModelError,
    VALID_OPENAI_MODELS,
    VALID_GEMINI_MODELS,
)
from app.schemas import GitHubIssue, AnalysisResult


class TestAIEngineOpenAI:
    """Tests for AIEngine with OpenAI provider"""

    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        with patch.dict("os.environ", {"AI_PROVIDER": "openai"}, clear=True):
            with pytest.raises(APIKeyError, match="API key not configured"):
                AIEngine()

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                "AI_PROVIDER": "openai",
            },
        ):
            engine = AIEngine()
            assert engine.api_key == "test_key_that_is_long_enough_12345"
            assert engine.model == "gpt-4o-mini"
            assert engine.provider == "openai"

    def test_init_with_invalid_model(self):
        """Test initialization with invalid model raises error"""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                "MODEL": "invalid-model",
                "AI_PROVIDER": "openai",
            },
        ):
            with pytest.raises(ModelError, match="Invalid model"):
                AIEngine()

    def test_init_with_valid_models(self):
        """Test initialization accepts all valid OpenAI models"""
        for model in VALID_OPENAI_MODELS:
            with patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                    "AI_PROVIDER": "openai",
                },
            ):
                engine = AIEngine(model=model)
                assert engine.model == model


class TestAIEngineGemini:
    """Tests for AIEngine with Gemini provider"""

    def test_init_without_gemini_api_key(self):
        """Test initialization without Gemini API key raises error"""
        with patch.dict("os.environ", {"AI_PROVIDER": "gemini"}, clear=True):
            with pytest.raises(APIKeyError, match="API key not configured"):
                AIEngine()

    def test_init_with_gemini_api_key(self):
        """Test initialization with Gemini API key"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "test_gemini_key_that_is_long_enough",
                "AI_PROVIDER": "gemini",
                "MODEL": "gemini-2.0-flash",
            },
            clear=True,
        ):
            with patch("app.ai_engine.genai") as mock_genai:
                engine = AIEngine()
                assert engine.api_key == "test_gemini_key_that_is_long_enough"
                assert engine.provider == "gemini"
                assert engine.model == "gemini-2.0-flash"
                mock_genai.configure.assert_called_once_with(
                    api_key="test_gemini_key_that_is_long_enough"
                )

    def test_init_with_google_api_key_fallback(self):
        """Test initialization falls back to GOOGLE_API_KEY"""
        with patch.dict(
            "os.environ",
            {
                "GOOGLE_API_KEY": "test_google_key_that_is_long_enough",
                "AI_PROVIDER": "gemini",
                "MODEL": "gemini-2.0-flash",
            },
            clear=True,
        ):
            with patch("app.ai_engine.genai"):
                engine = AIEngine()
                assert engine.api_key == "test_google_key_that_is_long_enough"

    def test_init_with_invalid_gemini_model(self):
        """Test initialization with invalid Gemini model raises error"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "test_gemini_key_that_is_long_enough",
                "AI_PROVIDER": "gemini",
                "MODEL": "invalid-model",
            },
        ):
            with patch("app.ai_engine.genai"):
                with pytest.raises(ModelError, match="Invalid model"):
                    AIEngine()

    def test_init_with_valid_gemini_models(self):
        """Test initialization accepts all valid Gemini models"""
        for model in VALID_GEMINI_MODELS:
            with patch.dict(
                "os.environ",
                {
                    "GEMINI_API_KEY": "test_gemini_key_that_is_long_enough",
                    "AI_PROVIDER": "gemini",
                },
            ):
                with patch("app.ai_engine.genai"):
                    engine = AIEngine(model=model)
                    assert engine.model == model

    def test_short_api_key_raises_error(self):
        """Test that short API keys raise an error"""
        with patch.dict(
            "os.environ", {"GEMINI_API_KEY": "short", "AI_PROVIDER": "gemini"}
        ):
            with pytest.raises(APIKeyError, match="invalid"):
                AIEngine()


class TestAIEngineCommon:
    """Common tests for AIEngine regardless of provider"""

    def test_build_prompt(self):
        """Test prompt building"""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                "AI_PROVIDER": "openai",
            },
        ):
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
                updated_at="2024-01-02T00:00:00Z",
            )

            prompt = engine._build_prompt(issue)

            assert "Test Issue Title" in prompt
            assert "Test issue body content" in prompt
            assert "Comment 1" in prompt

    def test_validate_result_with_valid_data(self):
        """Test result validation with valid data"""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                "AI_PROVIDER": "openai",
            },
        ):
            engine = AIEngine()

            result_data = {
                "summary": "Test summary",
                "root_cause": "Test root cause",
                "solution_steps": ["Step 1", "Step 2", "Step 3"],
                "checklist": ["Item 1", "Item 2", "Item 3"],
                "labels": ["bug", "enhancement"],
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
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                "AI_PROVIDER": "openai",
            },
        ):
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
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                "AI_PROVIDER": "openai",
            },
        ):
            engine = AIEngine()

            result_data = {
                "summary": "Test",
                "root_cause": "Test",
                "solution_steps": ["Step 1"],
                "checklist": ["Item 1"],
                "labels": ["bug", "invalid-label", "feature", "random"],
            }

            result = engine._validate_result(result_data)

            assert "bug" in result.labels
            assert "feature" in result.labels
            assert "invalid-label" not in result.labels
            assert "random" not in result.labels


class TestAIEngineAnalysis:
    """Tests for analyze_issue method"""

    @pytest.mark.asyncio
    async def test_analyze_issue_openai(self):
        """Test full issue analysis with OpenAI"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"summary": "Test", "root_cause": "Test", "solution_steps": ["Step 1"], "checklist": ["Item 1"], "labels": ["bug"]}'
                )
            )
        ]

        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key_that_is_long_enough_12345",
                "AI_PROVIDER": "openai",
            },
        ):
            engine = AIEngine()
            engine.client.chat.completions.create = AsyncMock(
                return_value=mock_response
            )

            issue = GitHubIssue(
                number=123,
                title="Test Issue",
                body="Test body",
                state="open",
                labels=[],
                url="https://github.com/owner/repo/issues/123",
                comments=[],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
            )

            result = await engine.analyze_issue(issue)

            assert isinstance(result, AnalysisResult)
            assert result.summary == "Test"

    @pytest.mark.asyncio
    async def test_analyze_issue_gemini(self):
        """Test full issue analysis with Gemini"""
        mock_response = MagicMock()
        mock_response.text = '{"summary": "Gemini Test", "root_cause": "Test", "solution_steps": ["Step 1"], "checklist": ["Item 1"], "labels": ["bug"]}'

        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "test_gemini_key_that_is_long_enough",
                "AI_PROVIDER": "gemini",
                "MODEL": "gemini-2.0-flash",
            },
            clear=True,
        ):
            with patch("app.ai_engine.genai") as mock_genai:
                mock_model = MagicMock()
                mock_model.generate_content.return_value = mock_response
                mock_genai.GenerativeModel.return_value = mock_model

                engine = AIEngine()

                issue = GitHubIssue(
                    number=123,
                    title="Test Issue",
                    body="Test body",
                    state="open",
                    labels=[],
                    url="https://github.com/owner/repo/issues/123",
                    comments=[],
                    created_at="2024-01-01T00:00:00Z",
                    updated_at="2024-01-02T00:00:00Z",
                )

                # Mock run_in_executor to return synchronously
                with patch("asyncio.get_event_loop") as mock_loop:
                    mock_loop.return_value.run_in_executor = AsyncMock(
                        return_value=mock_response
                    )
                    result = await engine.analyze_issue(issue)

                assert isinstance(result, AnalysisResult)
                assert result.summary == "Gemini Test"


class TestAIEngineProviderSelection:
    """Tests for provider selection logic"""

    def test_default_provider_is_openai(self):
        """Test that default provider is OpenAI when not specified"""
        with patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": "test_key_that_is_long_enough_12345"},
            clear=True,
        ):
            engine = AIEngine()
            assert engine.provider == "openai"

    def test_explicit_gemini_provider(self):
        """Test explicit Gemini provider selection"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "test_gemini_key_that_is_long_enough",
                "AI_PROVIDER": "gemini",
                "MODEL": "gemini-2.0-flash",
            },
            clear=True,
        ):
            with patch("app.ai_engine.genai"):
                engine = AIEngine()
                assert engine.provider == "gemini"

    def test_provider_from_constructor(self):
        """Test provider can be set via constructor"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "test_gemini_key_that_is_long_enough",
                "MODEL": "gemini-2.0-flash",
            },
            clear=True,
        ):
            with patch("app.ai_engine.genai"):
                engine = AIEngine(provider="gemini")
                assert engine.provider == "gemini"
