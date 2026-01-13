"""
Tests for database and repository functionality
"""

import os
import pytest
from unittest.mock import patch

# Set test database URL before importing modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database import (
    Base,
    AnalysisRecord,
    SimilarIssueRecord,
    get_engine,
    get_session,
    is_database_enabled,
    init_database,
)
from app.repository import AnalysisRepository
from app.schemas import AnalysisResult, SimilarIssue


@pytest.fixture(autouse=True)
def setup_database():
    """Reset database before each test"""
    # Reset the database module's cached state
    import app.database as db_module
    db_module._engine = None
    db_module._SessionLocal = None
    db_module.DATABASE_URL = "sqlite:///:memory:"
    db_module.DATABASE_ENABLED = True
    
    # Initialize database
    init_database()
    yield
    
    # Clean up
    session = get_session()
    if session:
        session.query(SimilarIssueRecord).delete()
        session.query(AnalysisRecord).delete()
        session.commit()
        session.close()


class TestDatabaseSetup:
    """Tests for database initialization"""

    def test_database_enabled(self):
        """Test that database is enabled when URL is set"""
        assert is_database_enabled() is True

    def test_get_engine_returns_engine(self):
        """Test that get_engine returns a valid engine"""
        engine = get_engine()
        assert engine is not None

    def test_get_session_returns_session(self):
        """Test that get_session returns a valid session"""
        session = get_session()
        assert session is not None
        session.close()

    def test_init_database_creates_tables(self):
        """Test that init_database creates tables"""
        result = init_database()
        assert result is True


class TestAnalysisRepository:
    """Tests for AnalysisRepository"""

    def test_is_available(self):
        """Test repository availability check"""
        assert AnalysisRepository.is_available() is True

    def test_save_analysis_creates_record(self):
        """Test saving an analysis creates a database record"""
        result = AnalysisResult(
            summary="Test summary",
            root_cause="Test root cause",
            solution_steps=["Step 1", "Step 2"],
            checklist=["Check 1", "Check 2"],
            labels=["bug"],
            similar_issues=[],
        )

        record_id = AnalysisRepository.save_analysis(
            repo="test/repo",
            issue_number=1,
            result=result,
            issue_title="Test Issue",
            ai_provider="openai",
        )

        assert record_id is not None
        assert record_id > 0

    def test_save_analysis_with_similar_issues(self):
        """Test saving analysis with similar issues"""
        result = AnalysisResult(
            summary="Test summary",
            root_cause="Test root cause",
            solution_steps=["Step 1"],
            checklist=["Check 1"],
            labels=["bug"],
            similar_issues=[
                SimilarIssue(
                    issue_number=42,
                    title="Similar Issue",
                    url="https://github.com/test/repo/issues/42",
                    similarity=0.85,
                ),
            ],
        )

        record_id = AnalysisRepository.save_analysis(
            repo="test/repo",
            issue_number=2,
            result=result,
        )

        # Retrieve and verify
        stored = AnalysisRepository.get_analysis("test/repo", 2)
        assert stored is not None
        assert len(stored["result"].similar_issues) == 1
        assert stored["result"].similar_issues[0].issue_number == 42

    def test_save_analysis_updates_existing(self):
        """Test that saving to same repo/issue updates the record"""
        result1 = AnalysisResult(
            summary="Original summary",
            root_cause="Original",
            solution_steps=["Step 1"],
            checklist=["Check 1"],
            labels=["bug"],
            similar_issues=[],
        )

        record_id1 = AnalysisRepository.save_analysis(
            repo="test/repo",
            issue_number=3,
            result=result1,
        )

        result2 = AnalysisResult(
            summary="Updated summary",
            root_cause="Updated",
            solution_steps=["New Step 1"],
            checklist=["New Check 1"],
            labels=["enhancement"],
            similar_issues=[],
        )

        record_id2 = AnalysisRepository.save_analysis(
            repo="test/repo",
            issue_number=3,
            result=result2,
        )

        # Should update same record
        assert record_id1 == record_id2

        # Verify updated content
        stored = AnalysisRepository.get_analysis("test/repo", 3)
        assert stored["result"].summary == "Updated summary"
        assert stored["result"].labels == ["enhancement"]

    def test_get_analysis_returns_stored_record(self):
        """Test retrieving a stored analysis"""
        result = AnalysisResult(
            summary="Test summary",
            root_cause="Test root cause",
            solution_steps=["Step 1"],
            checklist=["Check 1"],
            labels=["bug"],
            similar_issues=[],
        )

        AnalysisRepository.save_analysis(
            repo="test/repo",
            issue_number=4,
            result=result,
            issue_title="Test Issue",
            ai_provider="gemini",
        )

        stored = AnalysisRepository.get_analysis("test/repo", 4)

        assert stored is not None
        assert stored["repo"] == "test/repo"
        assert stored["issue_number"] == 4
        assert stored["issue_title"] == "Test Issue"
        assert stored["ai_provider"] == "gemini"
        assert stored["result"].summary == "Test summary"

    def test_get_analysis_returns_none_for_nonexistent(self):
        """Test that get_analysis returns None for non-existent records"""
        result = AnalysisRepository.get_analysis("nonexistent/repo", 999)
        assert result is None

    def test_get_history_returns_records(self):
        """Test retrieving analysis history"""
        # Create some test records
        for i in range(5):
            result = AnalysisResult(
                summary=f"Summary {i}",
                root_cause=f"Root cause {i}",
                solution_steps=["Step 1"],
                checklist=["Check 1"],
                labels=["bug"],
                similar_issues=[],
            )
            AnalysisRepository.save_analysis(
                repo="test/repo",
                issue_number=10 + i,
                result=result,
            )

        history = AnalysisRepository.get_history()

        assert len(history) >= 5

    def test_get_history_with_repo_filter(self):
        """Test filtering history by repo"""
        # Create records for different repos
        for repo in ["repo-a/test", "repo-b/test"]:
            result = AnalysisResult(
                summary="Summary",
                root_cause="Root cause",
                solution_steps=["Step 1"],
                checklist=["Check 1"],
                labels=["bug"],
                similar_issues=[],
            )
            AnalysisRepository.save_analysis(
                repo=repo,
                issue_number=1,
                result=result,
            )

        # Filter by repo
        history_a = AnalysisRepository.get_history(repo="repo-a/test")
        history_b = AnalysisRepository.get_history(repo="repo-b/test")

        assert len(history_a) == 1
        assert len(history_b) == 1
        assert history_a[0]["repo"] == "repo-a/test"

    def test_get_history_with_pagination(self):
        """Test history pagination"""
        # Create 10 records
        for i in range(10):
            result = AnalysisResult(
                summary=f"Summary {i}",
                root_cause="Root cause",
                solution_steps=["Step 1"],
                checklist=["Check 1"],
                labels=["bug"],
                similar_issues=[],
            )
            AnalysisRepository.save_analysis(
                repo="page/test",
                issue_number=100 + i,
                result=result,
            )

        # Get first page
        page1 = AnalysisRepository.get_history(repo="page/test", limit=5, offset=0)
        page2 = AnalysisRepository.get_history(repo="page/test", limit=5, offset=5)

        assert len(page1) == 5
        assert len(page2) == 5

    def test_delete_analysis_removes_record(self):
        """Test deleting an analysis"""
        result = AnalysisResult(
            summary="To be deleted",
            root_cause="Root cause",
            solution_steps=["Step 1"],
            checklist=["Check 1"],
            labels=["bug"],
            similar_issues=[],
        )

        AnalysisRepository.save_analysis(
            repo="delete/test",
            issue_number=99,
            result=result,
        )

        # Verify it exists
        stored = AnalysisRepository.get_analysis("delete/test", 99)
        assert stored is not None

        # Delete it
        deleted = AnalysisRepository.delete_analysis("delete/test", 99)
        assert deleted is True

        # Verify it's gone
        stored = AnalysisRepository.get_analysis("delete/test", 99)
        assert stored is None

    def test_delete_analysis_returns_false_for_nonexistent(self):
        """Test that delete returns False for non-existent records"""
        deleted = AnalysisRepository.delete_analysis("nonexistent/repo", 999)
        assert deleted is False

    def test_get_stats_returns_counts(self):
        """Test getting database statistics"""
        # Create some test data
        for i in range(3):
            result = AnalysisResult(
                summary="Summary",
                root_cause="Root cause",
                solution_steps=["Step 1"],
                checklist=["Check 1"],
                labels=["bug"],
                similar_issues=[],
            )
            AnalysisRepository.save_analysis(
                repo=f"stats/repo{i}",
                issue_number=1,
                result=result,
            )

        stats = AnalysisRepository.get_stats()

        assert stats["enabled"] is True
        assert stats["total_analyses"] >= 3
        assert stats["unique_repos"] >= 3


class TestDatabaseDisabled:
    """Tests for when database is disabled"""

    def test_repository_not_available_when_disabled(self):
        """Test that repository reports not available when DB disabled"""
        import app.database as db_module
        original_enabled = db_module.DATABASE_ENABLED
        
        db_module.DATABASE_ENABLED = False
        
        assert AnalysisRepository.is_available() is False
        
        db_module.DATABASE_ENABLED = original_enabled

    def test_save_returns_none_when_disabled(self):
        """Test that save returns None when DB is disabled"""
        import app.database as db_module
        original_enabled = db_module.DATABASE_ENABLED
        
        db_module.DATABASE_ENABLED = False
        
        result = AnalysisResult(
            summary="Test",
            root_cause="Test",
            solution_steps=["Step 1"],
            checklist=["Check 1"],
            labels=["bug"],
            similar_issues=[],
        )
        
        record_id = AnalysisRepository.save_analysis(
            repo="test/repo",
            issue_number=1,
            result=result,
        )
        
        assert record_id is None
        
        db_module.DATABASE_ENABLED = original_enabled

    def test_get_history_returns_empty_when_disabled(self):
        """Test that get_history returns empty list when DB is disabled"""
        import app.database as db_module
        original_enabled = db_module.DATABASE_ENABLED
        
        db_module.DATABASE_ENABLED = False
        
        history = AnalysisRepository.get_history()
        
        assert history == []
        
        db_module.DATABASE_ENABLED = original_enabled
