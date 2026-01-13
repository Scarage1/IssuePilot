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


class BatchAnalyzeRequest(BaseModel):
    """Request schema for /analyze/batch endpoint"""

    repo: str = Field(
        ...,
        description="Repository in format 'owner/repo'",
        pattern=r"^[\w.-]+/[\w.-]+$",
    )
    issue_numbers: List[int] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of issue numbers to analyze (max 10)"
    )
    github_token: Optional[str] = Field(
        None, description="Optional GitHub token for higher rate limits"
    )


class BatchAnalysisItem(BaseModel):
    """Single issue result in batch analysis"""

    issue_number: int
    success: bool
    result: Optional[AnalysisResult] = None
    error: Optional[str] = None


class BatchAnalysisResult(BaseModel):
    """Response schema for batch analysis"""

    repo: str
    total: int
    successful: int
    failed: int
    results: List[BatchAnalysisItem]


class ExportRequest(BaseModel):
    """Request schema for /export endpoint"""

    analysis: AnalysisResult
    repo: Optional[str] = Field(None, description="Repository name (optional)")
    issue_number: Optional[int] = Field(None, description="Issue number (optional)")


class ExportResponse(BaseModel):
    """Response schema for markdown export"""

    markdown: str


class DependencyStatus(BaseModel):
    """Schema for dependency health status"""

    openai_api_configured: bool = Field(
        ..., description="Whether OpenAI API key is configured"
    )
    github_api_accessible: bool = Field(
        ..., description="Whether GitHub API is accessible"
    )


class HealthResponse(BaseModel):
    """Response schema for health check"""

    status: str = "ok"
    version: str = "1.1.0"
    dependencies: Optional[DependencyStatus] = None
    cache_size: int = Field(default=0, description="Current number of cached entries")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")


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


class StoredAnalysis(BaseModel):
    """Schema for a stored analysis record"""

    id: int
    repo: str
    issue_number: int
    issue_title: Optional[str] = None
    result: AnalysisResult
    ai_provider: Optional[str] = None
    created_at: str
    updated_at: str


class AnalysisHistoryItem(BaseModel):
    """Schema for analysis history list item"""

    id: int
    repo: str
    issue_number: int
    issue_title: Optional[str] = None
    summary: str
    labels: List[str]
    ai_provider: Optional[str] = None
    created_at: str


class AnalysisHistoryResponse(BaseModel):
    """Response schema for analysis history"""

    items: List[AnalysisHistoryItem]
    total: int


class DatabaseStats(BaseModel):
    """Schema for database statistics"""

    enabled: bool
    total_analyses: Optional[int] = None
    unique_repos: Optional[int] = None
