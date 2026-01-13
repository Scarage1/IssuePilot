"""
Repository layer for database operations

Provides a clean interface for storing and retrieving analysis records.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from .database import (
    get_session,
    is_database_enabled,
    AnalysisRecord,
    SimilarIssueRecord,
)
from .schemas import AnalysisResult, SimilarIssue


class AnalysisRepository:
    """Repository for analysis records"""

    @staticmethod
    def is_available() -> bool:
        """Check if the repository is available (database enabled)"""
        return is_database_enabled()

    @staticmethod
    def save_analysis(
        repo: str,
        issue_number: int,
        result: AnalysisResult,
        issue_title: Optional[str] = None,
        ai_provider: Optional[str] = None,
    ) -> Optional[int]:
        """
        Save an analysis result to the database.
        
        Returns the record ID if successful, None if database is disabled.
        """
        if not is_database_enabled():
            return None

        session = get_session()
        if not session:
            return None

        try:
            # Check if record already exists for this repo/issue
            existing = (
                session.query(AnalysisRecord)
                .filter_by(repo=repo, issue_number=issue_number)
                .first()
            )

            if existing:
                # Update existing record
                existing.summary = result.summary
                existing.root_cause = result.root_cause
                existing.solution_steps = result.solution_steps
                existing.checklist = result.checklist
                existing.labels = result.labels
                existing.issue_title = issue_title
                existing.ai_provider = ai_provider
                existing.updated_at = datetime.utcnow()

                # Update similar issues
                session.query(SimilarIssueRecord).filter_by(
                    analysis_id=existing.id
                ).delete()
                
                for similar in result.similar_issues:
                    session.add(
                        SimilarIssueRecord(
                            analysis_id=existing.id,
                            issue_number=similar.issue_number,
                            title=similar.title,
                            url=similar.url,
                            similarity=similar.similarity,
                        )
                    )

                session.commit()
                return existing.id
            else:
                # Create new record
                record = AnalysisRecord(
                    repo=repo,
                    issue_number=issue_number,
                    issue_title=issue_title,
                    summary=result.summary,
                    root_cause=result.root_cause,
                    solution_steps=result.solution_steps,
                    checklist=result.checklist,
                    labels=result.labels,
                    ai_provider=ai_provider,
                )
                session.add(record)
                session.flush()  # Get the ID

                # Add similar issues
                for similar in result.similar_issues:
                    session.add(
                        SimilarIssueRecord(
                            analysis_id=record.id,
                            issue_number=similar.issue_number,
                            title=similar.title,
                            url=similar.url,
                            similarity=similar.similarity,
                        )
                    )

                session.commit()
                return record.id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_analysis(repo: str, issue_number: int) -> Optional[dict]:
        """
        Get a saved analysis by repo and issue number.
        
        Returns the analysis as a dict or None if not found.
        """
        if not is_database_enabled():
            return None

        session = get_session()
        if not session:
            return None

        try:
            record = (
                session.query(AnalysisRecord)
                .filter_by(repo=repo, issue_number=issue_number)
                .first()
            )

            if not record:
                return None

            return {
                "id": record.id,
                "repo": record.repo,
                "issue_number": record.issue_number,
                "issue_title": record.issue_title,
                "result": AnalysisResult(
                    summary=record.summary,
                    root_cause=record.root_cause,
                    solution_steps=record.solution_steps,
                    checklist=record.checklist,
                    labels=record.labels,
                    similar_issues=[
                        SimilarIssue(
                            issue_number=s.issue_number,
                            title=s.title,
                            url=s.url,
                            similarity=s.similarity,
                        )
                        for s in record.similar_issues
                    ],
                ),
                "ai_provider": record.ai_provider,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
            }

        finally:
            session.close()

    @staticmethod
    def get_history(
        repo: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[dict]:
        """
        Get analysis history, optionally filtered by repo.
        
        Returns a list of analysis summaries.
        """
        if not is_database_enabled():
            return []

        session = get_session()
        if not session:
            return []

        try:
            query = session.query(AnalysisRecord)

            if repo:
                query = query.filter_by(repo=repo)

            records = (
                query.order_by(desc(AnalysisRecord.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": r.id,
                    "repo": r.repo,
                    "issue_number": r.issue_number,
                    "issue_title": r.issue_title,
                    "summary": r.summary[:200] + "..." if len(r.summary) > 200 else r.summary,
                    "labels": r.labels,
                    "ai_provider": r.ai_provider,
                    "created_at": r.created_at.isoformat(),
                }
                for r in records
            ]

        finally:
            session.close()

    @staticmethod
    def delete_analysis(repo: str, issue_number: int) -> bool:
        """
        Delete an analysis record.
        
        Returns True if deleted, False if not found or database disabled.
        """
        if not is_database_enabled():
            return False

        session = get_session()
        if not session:
            return False

        try:
            record = (
                session.query(AnalysisRecord)
                .filter_by(repo=repo, issue_number=issue_number)
                .first()
            )

            if not record:
                return False

            session.delete(record)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_stats() -> dict:
        """Get database statistics"""
        if not is_database_enabled():
            return {"enabled": False}

        session = get_session()
        if not session:
            return {"enabled": False}

        try:
            total_analyses = session.query(AnalysisRecord).count()
            unique_repos = (
                session.query(AnalysisRecord.repo).distinct().count()
            )

            return {
                "enabled": True,
                "total_analyses": total_analyses,
                "unique_repos": unique_repos,
            }

        finally:
            session.close()
