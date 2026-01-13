"""
IssuePilot - AI-Powered GitHub Issue Assistant
Main FastAPI Application
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from cachetools import TTLCache
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .ai_engine import AIEngine
from .duplicate_finder import DuplicateFinder
from .github_client import GitHubClient
from .repository import AnalysisRepository
from .schemas import (
    AnalysisHistoryItem,
    AnalysisHistoryResponse,
    AnalysisResult,
    AnalyzeRequest,
    BatchAnalyzeRequest,
    BatchAnalysisItem,
    BatchAnalysisResult,
    DatabaseStats,
    DependencyStatus,
    ErrorResponse,
    ExportRequest,
    ExportResponse,
    HealthResponse,
    StoredAnalysis,
)
from .utils import generate_markdown_export, generate_html_export
from .webhook import (
    IssueWebhookPayload,
    WebhookResponse,
    WebhookConfig,
    get_webhook_config,
    verify_webhook_signature,
    should_analyze_issue,
    format_webhook_log,
)

# Load environment variables from .env file in parent directory
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
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
    logger.info(
        f"{status_emoji} {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)"
    )

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
        openai_api_configured=openai_configured, github_api_accessible=github_accessible
    )

    return HealthResponse(
        status="ok",
        version="1.1.0",
        dependencies=dependencies,
        cache_size=len(analysis_cache),
        cache_ttl=CACHE_TTL,
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

    logger.info(
        f"🔍 Analyzing {request.repo}#{request.issue_number} (cache={'bypass' if no_cache else 'miss'})"
    )

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
                logger.warning(
                    f"Issue not found: {request.repo}#{request.issue_number}"
                )
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

        # Save to database if enabled
        if AnalysisRepository.is_available():
            try:
                AnalysisRepository.save_analysis(
                    repo=request.repo,
                    issue_number=request.issue_number,
                    result=analysis,
                    issue_title=issue.title,
                    ai_provider=ai_engine.get_provider_name(),
                )
                logger.info(f"💾 Saved to database: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to save to database: {e}")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@app.post(
    "/analyze/batch",
    response_model=BatchAnalysisResult,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Analysis"],
)
async def analyze_batch(request: BatchAnalyzeRequest, http_request: Request):
    """
    Analyze multiple GitHub issues in batch.

    This endpoint processes up to 10 issues at once, returning results
    for each issue including any failures.

    Supports caching - use X-No-Cache header to bypass cache.

    Args:
        request: BatchAnalyzeRequest with repo and issue_numbers list
        http_request: HTTP request for cache control headers

    Returns:
        BatchAnalysisResult with results for all issues
    """
    no_cache = http_request.headers.get("X-No-Cache", "").lower() == "true"
    results: list[BatchAnalysisItem] = []
    successful = 0
    failed = 0

    logger.info(
        f"🔄 Batch analyzing {len(request.issue_numbers)} issues in {request.repo}"
    )

    try:
        # Initialize clients once for all issues
        github_client = GitHubClient(token=request.github_token)
        ai_engine = AIEngine()
        duplicate_finder = DuplicateFinder()

        # Pre-fetch all open issues for duplicate detection
        existing_issues = []
        try:
            existing_issues = await github_client.get_open_issues(
                request.repo, max_issues=50
            )
        except Exception as e:
            logger.warning(f"Could not fetch existing issues for duplicate detection: {e}")

        # Process each issue
        for issue_number in request.issue_numbers:
            cache_key = get_cache_key(request.repo, issue_number)

            # Check cache first
            if not no_cache and cache_key in analysis_cache:
                logger.info(f"📦 Cache hit for {cache_key}")
                results.append(BatchAnalysisItem(
                    issue_number=issue_number,
                    success=True,
                    result=analysis_cache[cache_key]
                ))
                successful += 1
                continue

            try:
                # Fetch issue
                issue = await github_client.get_issue(request.repo, issue_number)

                # Analyze with AI
                analysis = await ai_engine.analyze_issue(issue)

                # Find similar issues
                try:
                    similar_issues = await duplicate_finder.find_similar_issues(
                        issue, existing_issues, top_k=3
                    )
                    analysis.similar_issues = similar_issues
                except Exception as e:
                    logger.warning(f"Duplicate detection failed for #{issue_number}: {e}")

                # Cache the result
                analysis_cache[cache_key] = analysis

                results.append(BatchAnalysisItem(
                    issue_number=issue_number,
                    success=True,
                    result=analysis
                ))
                successful += 1
                logger.info(f"✅ Analyzed #{issue_number}")

            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    error_msg = f"Issue #{issue_number} not found"
                
                results.append(BatchAnalysisItem(
                    issue_number=issue_number,
                    success=False,
                    error=error_msg
                ))
                failed += 1
                logger.warning(f"❌ Failed to analyze #{issue_number}: {error_msg}")

        return BatchAnalysisResult(
            repo=request.repo,
            total=len(request.issue_numbers),
            successful=successful,
            failed=failed,
            results=results
        )

    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}",
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
        markdown = generate_markdown_export(
            request.analysis,
            repo=request.repo or "",
            issue_number=request.issue_number or 0
        )
        return ExportResponse(markdown=markdown)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@app.post("/export/html", tags=["Export"])
async def export_html(request: ExportRequest):
    """
    Export analysis result to HTML format.

    Args:
        request: ExportRequest with analysis data

    Returns:
        HTML content as string
    """
    try:
        logger.debug("Generating HTML export")
        html = generate_html_export(
            request.analysis,
            repo=request.repo or "",
            issue_number=request.issue_number or 0
        )
        return {"html": html}
    except Exception as e:
        logger.error(f"HTML export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTML export failed: {str(e)}",
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
    return {"message": "Cache cleared successfully", "entries_cleared": count}


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
        "keys": list(analysis_cache.keys()),
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


# =============================================================================
# Database / History Endpoints
# =============================================================================


@app.get("/history", response_model=AnalysisHistoryResponse, tags=["History"])
async def get_history(repo: str = None, limit: int = 50, offset: int = 0):
    """
    Get analysis history from the database.

    Database persistence is optional. If not configured, returns empty list.

    Args:
        repo: Optional repository filter (format: owner/repo)
        limit: Maximum number of records to return (default 50)
        offset: Number of records to skip (for pagination)

    Returns:
        AnalysisHistoryResponse with list of analysis summaries
    """
    if not AnalysisRepository.is_available():
        return AnalysisHistoryResponse(items=[], total=0)

    try:
        items = AnalysisRepository.get_history(repo=repo, limit=limit, offset=offset)
        return AnalysisHistoryResponse(
            items=[AnalysisHistoryItem(**item) for item in items],
            total=len(items)
        )
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get history: {str(e)}",
        )


@app.get(
    "/history/{repo:path}/{issue_number}",
    response_model=StoredAnalysis,
    responses={404: {"model": ErrorResponse}},
    tags=["History"],
)
async def get_stored_analysis(repo: str, issue_number: int):
    """
    Get a stored analysis by repository and issue number.

    Args:
        repo: Repository (format: owner/repo)
        issue_number: Issue number

    Returns:
        StoredAnalysis with full analysis data
    """
    if not AnalysisRepository.is_available():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database not configured",
        )

    try:
        record = AnalysisRepository.get_analysis(repo, issue_number)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No stored analysis found for {repo}#{issue_number}",
            )
        return StoredAnalysis(**record)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stored analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}",
        )


@app.delete(
    "/history/{repo:path}/{issue_number}",
    responses={404: {"model": ErrorResponse}},
    tags=["History"],
)
async def delete_stored_analysis(repo: str, issue_number: int):
    """
    Delete a stored analysis by repository and issue number.

    Args:
        repo: Repository (format: owner/repo)
        issue_number: Issue number

    Returns:
        Confirmation message
    """
    if not AnalysisRepository.is_available():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database not configured",
        )

    try:
        deleted = AnalysisRepository.delete_analysis(repo, issue_number)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No stored analysis found for {repo}#{issue_number}",
            )
        logger.info(f"🗑️ Deleted stored analysis for {repo}#{issue_number}")
        return {"message": f"Deleted analysis for {repo}#{issue_number}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete analysis: {str(e)}",
        )


@app.get("/database/stats", response_model=DatabaseStats, tags=["Utilities"])
async def database_stats():
    """
    Get database statistics.

    Returns:
        DatabaseStats with database status and counts
    """
    stats = AnalysisRepository.get_stats()
    return DatabaseStats(**stats)


# =============================================================================
# Webhook Endpoints
# =============================================================================


async def analyze_issue_background(repo: str, issue_number: int, github_token: str = None):
    """Background task to analyze an issue from a webhook"""
    try:
        logger.info(f"🔄 Background analysis started for {repo}#{issue_number}")
        
        # Initialize clients
        github_client = GitHubClient(token=github_token)
        ai_engine = AIEngine()
        duplicate_finder = DuplicateFinder()
        
        # Fetch issue
        issue = await github_client.get_issue(repo, issue_number)
        
        # Analyze with AI
        analysis = await ai_engine.analyze_issue(issue)
        
        # Find similar issues
        try:
            existing_issues = await github_client.get_open_issues(repo, max_issues=50)
            similar_issues = await duplicate_finder.find_similar_issues(
                issue, existing_issues, top_k=3
            )
            analysis.similar_issues = similar_issues
        except Exception as e:
            logger.warning(f"Duplicate detection failed: {e}")
        
        # Cache the result
        cache_key = get_cache_key(repo, issue_number)
        analysis_cache[cache_key] = analysis
        
        # Save to database if enabled
        if AnalysisRepository.is_available():
            AnalysisRepository.save_analysis(
                repo=repo,
                issue_number=issue_number,
                result=analysis,
                issue_title=issue.title,
                ai_provider=ai_engine.get_provider_name(),
            )
            logger.info(f"💾 Saved webhook analysis to database: {repo}#{issue_number}")
        
        logger.info(f"✅ Background analysis completed for {repo}#{issue_number}")
        
    except Exception as e:
        logger.error(f"❌ Background analysis failed for {repo}#{issue_number}: {e}")


@app.post(
    "/webhook/github",
    response_model=WebhookResponse,
    tags=["Webhook"],
)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    x_github_event: str = Header(None, alias="X-GitHub-Event"),
):
    """
    GitHub webhook endpoint for automatic issue analysis.

    This endpoint receives GitHub webhook events and automatically
    analyzes new or updated issues based on configuration.

    Setup:
    1. Set GITHUB_WEBHOOK_SECRET environment variable
    2. Configure webhook in GitHub repo settings:
       - Payload URL: https://your-domain/webhook/github
       - Content type: application/json
       - Secret: same as GITHUB_WEBHOOK_SECRET
       - Events: Issues

    Configuration environment variables:
    - GITHUB_WEBHOOK_SECRET: Secret for signature verification
    - WEBHOOK_AUTO_ANALYZE_OPEN: Auto-analyze on issue open (default: true)
    - WEBHOOK_AUTO_ANALYZE_EDIT: Auto-analyze on issue edit (default: false)
    - WEBHOOK_AUTO_ANALYZE_LABEL: Auto-analyze on label add (default: false)
    - WEBHOOK_REQUIRED_LABEL: Only analyze if this label is present
    - WEBHOOK_EXCLUDED_LABELS: Comma-separated list of labels to skip

    Returns:
        WebhookResponse with status and analysis info
    """
    config = get_webhook_config()
    
    # Check if webhooks are enabled
    if not config.enabled:
        logger.warning("Webhook received but not configured (no secret)")
        return WebhookResponse(
            status="skipped",
            message="Webhooks not configured",
            analysis_triggered=False,
        )
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature
    if not verify_webhook_signature(body, x_hub_signature_256 or ""):
        logger.warning("Webhook signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )
    
    # Only handle issue events
    if x_github_event != "issues":
        return WebhookResponse(
            status="ignored",
            message=f"Event type '{x_github_event}' not handled",
            analysis_triggered=False,
        )
    
    # Parse payload
    try:
        payload_dict = await request.json()
        payload = IssueWebhookPayload(**payload_dict)
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid webhook payload: {str(e)}",
        )
    
    logger.info(f"📨 Webhook received: {format_webhook_log(payload)}")
    
    # Check if we should analyze
    should_analyze, reason = should_analyze_issue(payload, config)
    
    if not should_analyze:
        logger.info(f"⏭️ Skipping analysis: {reason}")
        return WebhookResponse(
            status="skipped",
            message=reason,
            action=payload.action,
            repo=payload.repository.full_name,
            issue_number=payload.issue.number,
            analysis_triggered=False,
        )
    
    # Trigger background analysis
    repo = payload.repository.full_name
    issue_number = payload.issue.number
    
    # Get GitHub token from environment for webhook requests
    github_token = os.getenv("GITHUB_TOKEN")
    
    background_tasks.add_task(
        analyze_issue_background,
        repo=repo,
        issue_number=issue_number,
        github_token=github_token,
    )
    
    logger.info(f"🚀 Triggered background analysis for {repo}#{issue_number}")
    
    return WebhookResponse(
        status="accepted",
        message=reason,
        action=payload.action,
        repo=repo,
        issue_number=issue_number,
        analysis_triggered=True,
    )


@app.get("/webhook/config", response_model=WebhookConfig, tags=["Webhook"])
async def webhook_config():
    """
    Get current webhook configuration.

    Returns information about webhook settings without exposing secrets.

    Returns:
        WebhookConfig with current settings
    """
    return get_webhook_config()


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
