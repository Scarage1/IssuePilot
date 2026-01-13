"""
Pydantic schemas for IssuePilot API
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SimilarIssue(BaseModel):
    """Schema for similar issue results"""

    issue_number: int
    title: str
    url: str
    similarity: float = Field(..., ge=0, le=1)


class AnalyzeRequest(BaseModel):
    """Request schema for /analyze endpoint"""

    repo: str = Field(
        ...,
        description="Repository in format 'owner/repo'",
        pattern=r"^[\w.-]+/[\w.-]+$",
    )
    issue_number: int = Field(..., gt=0, description="Issue number to analyze")
    github_token: Optional[str] = Field(
        None, description="Optional GitHub token for higher rate limits"
    )


class AnalysisResult(BaseModel):
    """Response schema for issue analysis"""

    summary: str
    root_cause: str
    solution_steps: List[str]
    checklist: List[str]
    labels: List[str]
    similar_issues: List[SimilarIssue] = []


class ExportRequest(BaseModel):
    """Request schema for /export endpoint"""

    analysis: AnalysisResult


class ExportResponse(BaseModel):
    """Response schema for markdown export"""

    markdown: str


class HealthResponse(BaseModel):
    """Response schema for health check"""

    status: str = "ok"


class GitHubIssue(BaseModel):
    """Schema for GitHub issue data"""

    number: int
    title: str
    body: Optional[str] = ""
    state: str
    labels: List[str] = []
    url: str
    comments: List[str] = []
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    """Schema for error responses"""

    error: str
    detail: Optional[str] = None
