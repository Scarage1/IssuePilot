"""
Tests for Utility Functions
"""

import pytest
from app.utils import (
    validate_repo_format,
    parse_repo,
    truncate_text,
    clean_json_response,
    generate_markdown_export,
    extract_code_blocks,
    sanitize_input,
)
from app.schemas import AnalysisResult, SimilarIssue


class TestValidateRepoFormat:
    """Tests for repo format validation"""

    def test_valid_format(self):
        """Test valid repo formats"""
        assert validate_repo_format("facebook/react") is True
        assert validate_repo_format("vercel/next.js") is True
        assert validate_repo_format("owner-name/repo-name") is True
        assert validate_repo_format("owner.name/repo.name") is True

    def test_invalid_format(self):
        """Test invalid repo formats"""
        assert validate_repo_format("invalid") is False
        assert validate_repo_format("too/many/slashes") is False
        assert validate_repo_format("") is False
        assert validate_repo_format("/repo") is False
        assert validate_repo_format("owner/") is False


class TestParseRepo:
    """Tests for repo parsing"""

    def test_valid_parse(self):
        """Test parsing valid repo strings"""
        owner, repo = parse_repo("facebook/react")
        assert owner == "facebook"
        assert repo == "react"

    def test_invalid_parse(self):
        """Test parsing invalid repo strings"""
        with pytest.raises(ValueError):
            parse_repo("invalid-format")


class TestTruncateText:
    """Tests for text truncation"""

    def test_short_text(self):
        """Test that short text is not truncated"""
        text = "Short text"
        result = truncate_text(text, 100)
        assert result == text

    def test_long_text(self):
        """Test that long text is truncated"""
        text = "This is a very long text " * 100
        result = truncate_text(text, 100)
        assert len(result) <= 103  # 100 + "..."
        assert result.endswith("...")

    def test_truncate_at_word_boundary(self):
        """Test truncation at word boundary"""
        text = "word1 word2 word3 word4 word5"
        result = truncate_text(text, 20)
        assert " " not in result[-3:]  # Should not end mid-word


class TestCleanJsonResponse:
    """Tests for JSON response cleaning"""

    def test_clean_json(self):
        """Test parsing clean JSON"""
        response = '{"key": "value"}'
        result = clean_json_response(response)
        assert result == {"key": "value"}

    def test_json_in_code_block(self):
        """Test extracting JSON from code block"""
        response = '```json\n{"key": "value"}\n```'
        result = clean_json_response(response)
        assert result == {"key": "value"}

    def test_json_with_whitespace(self):
        """Test JSON with extra whitespace"""
        response = '  \n{"key": "value"}\n  '
        result = clean_json_response(response)
        assert result == {"key": "value"}

    def test_invalid_json(self):
        """Test invalid JSON raises error"""
        response = "not valid json"
        with pytest.raises(ValueError, match="Failed to parse"):
            clean_json_response(response)


class TestGenerateMarkdownExport:
    """Tests for markdown export generation"""

    def test_basic_export(self):
        """Test basic markdown export"""
        analysis = AnalysisResult(
            summary="Test summary",
            root_cause="Test root cause",
            solution_steps=["Step 1", "Step 2"],
            checklist=["Item 1", "Item 2"],
            labels=["bug"],
            similar_issues=[],
        )

        markdown = generate_markdown_export(analysis)

        assert "# 🔍 Issue Analysis Report" in markdown
        assert "Test summary" in markdown
        assert "Test root cause" in markdown
        assert "Step 1" in markdown
        assert "[ ] Item 1" in markdown
        assert "`bug`" in markdown

    def test_export_with_repo_info(self):
        """Test export with repository info"""
        analysis = AnalysisResult(
            summary="Summary",
            root_cause="Root cause",
            solution_steps=["Step 1"],
            checklist=["Item 1"],
            labels=["bug"],
            similar_issues=[],
        )

        markdown = generate_markdown_export(
            analysis, repo="owner/repo", issue_number=123
        )

        assert "owner/repo" in markdown
        assert "#123" in markdown

    def test_export_with_similar_issues(self):
        """Test export with similar issues"""
        analysis = AnalysisResult(
            summary="Summary",
            root_cause="Root cause",
            solution_steps=["Step 1"],
            checklist=["Item 1"],
            labels=["bug"],
            similar_issues=[
                SimilarIssue(
                    issue_number=100,
                    title="Similar Issue",
                    url="https://github.com/owner/repo/issues/100",
                    similarity=0.85,
                )
            ],
        )

        markdown = generate_markdown_export(analysis)

        assert "Similar Issues" in markdown
        assert "Similar Issue" in markdown
        assert "85%" in markdown


class TestExtractCodeBlocks:
    """Tests for code block extraction"""

    def test_single_code_block(self):
        """Test extracting single code block"""
        text = "Some text\n```python\nprint('hello')\n```\nMore text"
        blocks = extract_code_blocks(text)

        assert len(blocks) == 1
        assert blocks[0]["language"] == "python"
        assert "print('hello')" in blocks[0]["code"]

    def test_multiple_code_blocks(self):
        """Test extracting multiple code blocks"""
        text = "```js\nconsole.log('hi');\n```\n\n```python\nprint('hi')\n```"
        blocks = extract_code_blocks(text)

        assert len(blocks) == 2
        assert blocks[0]["language"] == "js"
        assert blocks[1]["language"] == "python"

    def test_no_code_blocks(self):
        """Test text with no code blocks"""
        text = "Just plain text without any code blocks"
        blocks = extract_code_blocks(text)

        assert len(blocks) == 0

    def test_code_block_without_language(self):
        """Test code block without language specified"""
        text = "```\nsome code\n```"
        blocks = extract_code_blocks(text)

        assert len(blocks) == 1
        assert blocks[0]["language"] == "text"


class TestSanitizeInput:
    """Tests for input sanitization"""

    def test_clean_input(self):
        """Test that clean input passes through"""
        text = "Clean input text"
        result = sanitize_input(text)
        assert result == text

    def test_remove_null_bytes(self):
        """Test removal of null bytes"""
        text = "Text\x00with\x00nulls"
        result = sanitize_input(text)
        assert "\x00" not in result
        assert result == "Textwithnulls"

    def test_length_limit(self):
        """Test length limiting"""
        text = "a" * 100000
        result = sanitize_input(text)
        assert len(result) <= 50000

    def test_empty_input(self):
        """Test empty input"""
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""
