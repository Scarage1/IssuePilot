"""
IssuePilot - AI-Powered GitHub Issue Assistant
Main FastAPI Application
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache

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
    DependencyStatus,
)
from .utils import generate_markdown_export

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("issuepilot")

# Cache configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))
analysis_cache: TTLCache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("🚀 IssuePilot is starting up...")
    logger.info(f"Log level: {LOG_LEVEL}")
    logger.info(f"Cache TTL: {CACHE_TTL}s, Max size: {CACHE_MAX_SIZE}")
    yield
    # Shutdown
    logger.info("👋 IssuePilot is shutting down...")
    analysis_cache.clear()


# Initialize FastAPI app
app = FastAPI(
    title="IssuePilot",
    description="AI-powered GitHub issue analysis assistant for open-source maintainers and contributors",
    version="1.1.0",
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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests and responses"""
    start_time = time.time()
    
    # Log incoming request (exclude sensitive headers)
    logger.info(f"📥 {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    status_emoji = "✅" if response.status_code < 400 else "❌"
    logger.info(f"{status_emoji} {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    
    return response


def get_cache_key(repo: str, issue_number: int) -> str:
    """Generate cache key for analysis"""
    return f"{repo}:{issue_number}"


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    Includes dependency status for monitoring.

    Returns:
        HealthResponse with status, version, and dependency information
    """
    # Check OpenAI API key configuration
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    # Check GitHub API accessibility (optional, lightweight check)
    github_accessible = True
    try:
        github_client = GitHubClient()
        rate_info = await github_client.check_rate_limit()
        github_accessible = rate_info.get("remaining", 0) > 0
    except Exception as e:
        logger.warning(f"GitHub API check failed: {e}")
        github_accessible = False
    
    dependencies = DependencyStatus(
        openai_api_configured=openai_configured,
        github_api_accessible=github_accessible
    )
    
    return HealthResponse(
        status="ok",
        version="1.1.0",
        dependencies=dependencies,
        cache_size=len(analysis_cache),
        cache_ttl=CACHE_TTL
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        Welcome message and API info
    """
    return {
        "name": "IssuePilot",
        "version": "1.1.0",
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
async def analyze_issue(request: AnalyzeRequest, http_request: Request):
    """
    Analyze a GitHub issue and return structured insights.

    This endpoint:
    - Fetches issue details from GitHub
    - Generates AI-powered summary and analysis
    - Identifies potential root cause
    - Suggests solution steps and developer checklist
    - Recommends labels
    - Finds similar issues for duplicate detection

    Supports caching - use X-No-Cache header to bypass cache.

    Args:
        request: AnalyzeRequest with repo and issue_number
        http_request: HTTP request for cache control headers

    Returns:
        AnalysisResult with complete analysis
    """
    cache_key = get_cache_key(request.repo, request.issue_number)
    no_cache = http_request.headers.get("X-No-Cache", "").lower() == "true"
    
    # Check cache first (unless bypassed)
    if not no_cache and cache_key in analysis_cache:
        logger.info(f"📦 Cache hit for {cache_key}")
        return analysis_cache[cache_key]
    
    logger.info(f"🔍 Analyzing {request.repo}#{request.issue_number} (cache={'bypass' if no_cache else 'miss'})")
    
    try:
        # Initialize clients
        github_client = GitHubClient(token=request.github_token)
        ai_engine = AIEngine()
        duplicate_finder = DuplicateFinder()

        # Fetch issue from GitHub
        try:
            issue = await github_client.get_issue(request.repo, request.issue_number)
            logger.debug(f"Fetched issue: {issue.title}")
        except Exception as e:
            if "404" in str(e):
                logger.warning(f"Issue not found: {request.repo}#{request.issue_number}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Issue #{request.issue_number} not found in {request.repo}",
                )
            logger.error(f"GitHub API error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch issue: {str(e)}",
            )

        # Analyze issue with AI
        try:
            analysis = await ai_engine.analyze_issue(issue)
            logger.debug("AI analysis completed")
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
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
            logger.debug(f"Found {len(similar_issues)} similar issues")
        except Exception as e:
            # Don't fail if duplicate detection fails, just log
            logger.warning(f"Duplicate detection failed: {e}")

        # Store in cache
        analysis_cache[cache_key] = analysis
        logger.info(f"💾 Cached result for {cache_key}")
        
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
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
        logger.debug("Generating markdown export")
        markdown = generate_markdown_export(request.analysis)
        return ExportResponse(markdown=markdown)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@app.delete("/cache", tags=["Utilities"])
async def clear_cache():
    """
    Clear the analysis cache.

    Returns:
        Confirmation of cache clear with count of cleared items
    """
    count = len(analysis_cache)
    analysis_cache.clear()
    logger.info(f"🗑️ Cache cleared ({count} entries)")
    return {"message": f"Cache cleared successfully", "entries_cleared": count}


@app.get("/cache/stats", tags=["Utilities"])
async def cache_stats():
    """
    Get cache statistics.

    Returns:
        Cache size, TTL, and current entries
    """
    return {
        "size": len(analysis_cache),
        "max_size": CACHE_MAX_SIZE,
        "ttl_seconds": CACHE_TTL,
        "keys": list(analysis_cache.keys())
    }


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
        logger.debug(f"Rate limit: {rate_limit}")
        return rate_limit
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check rate limit: {str(e)}",
        )


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
