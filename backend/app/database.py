"""
Database models and configuration for IssuePilot

Uses SQLAlchemy with SQLite for persistence.
Database is optional - the app works without it.
"""

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import StaticPool

# Check if database is enabled
DATABASE_URL = os.getenv("DATABASE_URL", "")
DATABASE_ENABLED = bool(DATABASE_URL)

Base = declarative_base()


class AnalysisRecord(Base):
    """Stored analysis results"""

    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo = Column(String(255), nullable=False, index=True)
    issue_number = Column(Integer, nullable=False, index=True)
    issue_title = Column(String(500), nullable=True)
    
    # Analysis results
    summary = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    solution_steps = Column(JSON, nullable=False)  # List[str]
    checklist = Column(JSON, nullable=False)  # List[str]
    labels = Column(JSON, nullable=False)  # List[str]
    
    # Metadata
    ai_provider = Column(String(50), nullable=True)  # "openai" or "gemini"
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    similar_issues = relationship(
        "SimilarIssueRecord",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<AnalysisRecord {self.repo}#{self.issue_number}>"


class SimilarIssueRecord(Base):
    """Stored similar issues for an analysis"""

    __tablename__ = "similar_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analysis_records.id"), nullable=False)
    issue_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)
    similarity = Column(Float, nullable=False)

    analysis = relationship("AnalysisRecord", back_populates="similar_issues")

    def __repr__(self):
        return f"<SimilarIssueRecord #{self.issue_number} ({self.similarity:.2f})>"


# Database engine and session (initialized lazily)
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the database engine"""
    global _engine
    if _engine is None and DATABASE_ENABLED:
        # Use SQLite with check_same_thread=False for async compatibility
        if DATABASE_URL.startswith("sqlite"):
            _engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            _engine = create_engine(DATABASE_URL)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=_engine)
    return _engine


def get_session():
    """Get a database session"""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        if engine:
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal() if _SessionLocal else None


def is_database_enabled() -> bool:
    """Check if database is enabled and accessible"""
    return DATABASE_ENABLED and get_engine() is not None


def init_database():
    """Initialize the database (create tables)"""
    engine = get_engine()
    if engine:
        Base.metadata.create_all(bind=engine)
        return True
    return False
