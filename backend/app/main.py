"""
IssuePilot - AI-Powered GitHub Issue Assistant
Main FastAPI Application
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .ai_engine import AIEngine
from .duplicate_finder import DuplicateFinder
from .github_client import GitHubClient
from .schemas import (
    AnalysisResult,
    AnalyzeRequest,
    ErrorResponse,
    ExportRequest,
    ExportResponse,
    HealthResponse,
)
from .utils import generate_markdown_export

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("🚀 IssuePilot is starting up...")
    yield
    # Shutdown
    print("👋 IssuePilot is shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="IssuePilot",
    description="AI-powered GitHub issue analysis assistant for open-source maintainers and contributors",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.

    Returns:
        HealthResponse with status "ok"
    """
    return HealthResponse(status="ok")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        Welcome message and API info
    """
    return {
        "name": "IssuePilot",
        "version": "1.0.0",
        "description": "AI-powered GitHub issue analysis assistant",
        "docs": "/docs",
        "health": "/health",
    }


@app.post(
    "/analyze",
    response_model=AnalysisResult,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Analysis"],
)
async def analyze_issue(request: AnalyzeRequest):
    """
    Analyze a GitHub issue and return structured insights.

    This endpoint:
    - Fetches issue details from GitHub
    - Generates AI-powered summary and analysis
    - Identifies potential root cause
    - Suggests solution steps and developer checklist
    - Recommends labels
    - Finds similar issues for duplicate detection

    Args:
        request: AnalyzeRequest with repo and issue_number

    Returns:
        AnalysisResult with complete analysis
    """
    try:
        # Initialize clients
        github_client = GitHubClient(token=request.github_token)
        ai_engine = AIEngine()
        duplicate_finder = DuplicateFinder()

        # Fetch issue from GitHub
        try:
            issue = await github_client.get_issue(request.repo, request.issue_number)
        except Exception as e:
            if "404" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Issue #{request.issue_number} not found in {request.repo}",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch issue: {str(e)}",
            )

        # Analyze issue with AI
        try:
            analysis = await ai_engine.analyze_issue(issue)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI analysis failed: {str(e)}",
            )

        # Find similar issues
        try:
            existing_issues = await github_client.get_open_issues(
                request.repo, max_issues=50
            )
            similar_issues = await duplicate_finder.find_similar_issues(
                issue, existing_issues, top_k=3
            )
            analysis.similar_issues = similar_issues
        except Exception as e:
            # Don't fail if duplicate detection fails, just log
            print(f"Warning: Duplicate detection failed: {e}")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@app.post("/export", response_model=ExportResponse, tags=["Export"])
async def export_markdown(request: ExportRequest):
    """
    Export analysis result to markdown format.

    Args:
        request: ExportRequest with analysis data

    Returns:
        ExportResponse with formatted markdown
    """
    try:
        markdown = generate_markdown_export(request.analysis)
        return ExportResponse(markdown=markdown)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@app.get("/rate-limit", tags=["Utilities"])
async def check_rate_limit(github_token: str = None):
    """
    Check GitHub API rate limit status.

    Args:
        github_token: Optional GitHub token

    Returns:
        Rate limit information
    """
    try:
        github_client = GitHubClient(token=github_token)
        rate_limit = await github_client.check_rate_limit()
        return rate_limit
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check rate limit: {str(e)}",
        )


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
