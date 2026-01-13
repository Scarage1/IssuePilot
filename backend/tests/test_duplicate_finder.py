"""
Tests for Duplicate Finder
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.duplicate_finder import DuplicateFinder
from app.schemas import GitHubIssue, SimilarIssue


class TestDuplicateFinder:
    """Tests for DuplicateFinder class"""

    def test_init_with_embeddings(self):
        """Test initialization with embeddings enabled"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            finder = DuplicateFinder(use_embeddings=True)
            assert finder.use_embeddings is True
            assert finder.similarity_threshold == 0.75

    def test_init_without_embeddings(self):
        """Test initialization with TF-IDF fallback"""
        finder = DuplicateFinder(use_embeddings=False)
        assert finder.use_embeddings is False
        assert finder.vectorizer is not None

    def test_preprocess_text(self):
        """Test text preprocessing"""
        finder = DuplicateFinder(use_embeddings=False)
        
        text = "Hello World! Check this URL: https://example.com ```code block```"
        processed = finder._preprocess_text(text)
        
        assert "hello world" in processed
        assert "https" not in processed
        assert "```" not in processed

    def test_combine_issue_text(self):
        """Test combining title and body"""
        finder = DuplicateFinder(use_embeddings=False)
        
        combined = finder._combine_issue_text("Bug Title", "Bug description here")
        
        assert "bug title" in combined
        assert "bug description" in combined

    def test_tfidf_similarity(self):
        """Test TF-IDF similarity calculation"""
        finder = DuplicateFinder(use_embeddings=False)
        
        target = "react component rendering issue"
        comparisons = [
            "react component rendering problem",
            "python database connection",
            "react jsx rendering bug"
        ]
        
        similarities = finder._compute_tfidf_similarity(target, comparisons)
        
        assert len(similarities) == 3
        # First and third should have higher similarity
        assert similarities[0] > similarities[1]
        assert similarities[2] > similarities[1]

    def test_check_exact_duplicate_found(self):
        """Test exact duplicate detection when found"""
        finder = DuplicateFinder(use_embeddings=False)
        
        issue = GitHubIssue(
            number=123,
            title="Bug: App crashes on startup",
            body="Description",
            state="open",
            labels=[],
            url="https://github.com/owner/repo/issues/123",
            comments=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z"
        )
        
        existing_issues = [
            {"number": 100, "title": "Bug: App crashes on startup", "body": "Other desc", "url": "url1"},
            {"number": 101, "title": "Different issue", "body": "Body", "url": "url2"}
        ]
        
        duplicate = finder.check_exact_duplicate(issue, existing_issues)
        
        assert duplicate is not None
        assert duplicate["number"] == 100

    def test_check_exact_duplicate_not_found(self):
        """Test exact duplicate detection when not found"""
        finder = DuplicateFinder(use_embeddings=False)
        
        issue = GitHubIssue(
            number=123,
            title="Unique issue title",
            body="Description",
            state="open",
            labels=[],
            url="https://github.com/owner/repo/issues/123",
            comments=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z"
        )
        
        existing_issues = [
            {"number": 100, "title": "Different title", "body": "Desc", "url": "url1"},
            {"number": 101, "title": "Another title", "body": "Body", "url": "url2"}
        ]
        
        duplicate = finder.check_exact_duplicate(issue, existing_issues)
        
        assert duplicate is None

    @pytest.mark.asyncio
    async def test_find_similar_issues_tfidf(self):
        """Test finding similar issues using TF-IDF"""
        finder = DuplicateFinder(use_embeddings=False, similarity_threshold=0.3)
        
        issue = GitHubIssue(
            number=123,
            title="React component not rendering",
            body="The component does not render properly",
            state="open",
            labels=[],
            url="https://github.com/owner/repo/issues/123",
            comments=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z"
        )
        
        existing_issues = [
            {"number": 100, "title": "React component render issue", "body": "Component rendering fails", "url": "url1"},
            {"number": 101, "title": "Python import error", "body": "Cannot import module", "url": "url2"},
            {"number": 102, "title": "Component not showing", "body": "React component invisible", "url": "url3"}
        ]
        
        similar = await finder.find_similar_issues(issue, existing_issues, top_k=2)
        
        assert isinstance(similar, list)
        for item in similar:
            assert isinstance(item, SimilarIssue)

    @pytest.mark.asyncio
    async def test_find_similar_issues_empty_list(self):
        """Test finding similar issues with empty existing issues"""
        finder = DuplicateFinder(use_embeddings=False)
        
        issue = GitHubIssue(
            number=123,
            title="Test issue",
            body="Test body",
            state="open",
            labels=[],
            url="https://github.com/owner/repo/issues/123",
            comments=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z"
        )
        
        similar = await finder.find_similar_issues(issue, [], top_k=3)
        
        assert similar == []

    @pytest.mark.asyncio
    async def test_find_similar_issues_excludes_same_issue(self):
        """Test that the same issue is excluded from results"""
        finder = DuplicateFinder(use_embeddings=False, similarity_threshold=0.0)
        
        issue = GitHubIssue(
            number=123,
            title="Test issue",
            body="Test body",
            state="open",
            labels=[],
            url="https://github.com/owner/repo/issues/123",
            comments=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z"
        )
        
        existing_issues = [
            {"number": 123, "title": "Test issue", "body": "Test body", "url": "url1"},
            {"number": 124, "title": "Other issue", "body": "Other body", "url": "url2"}
        ]
        
        similar = await finder.find_similar_issues(issue, existing_issues, top_k=3)
        
        for item in similar:
            assert item.issue_number != 123
