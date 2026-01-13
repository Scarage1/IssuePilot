# IssuePilot API Documentation

Complete API reference for the IssuePilot backend service.

## Base URL

```
http://localhost:8000
```

---

## Authentication

IssuePilot does not require authentication for its own API. However, you can optionally provide a GitHub token for higher rate limits when fetching issues.

---

## Endpoints

### Health Check

Check if the service is running.

```http
GET /health
```

#### Response

```json
{
  "status": "ok"
}
```

| Status Code | Description |
|-------------|-------------|
| 200 | Service is healthy |

---

### Root

Get API information.

```http
GET /
```

#### Response

```json
{
  "name": "IssuePilot",
  "version": "1.0.0",
  "description": "AI-powered GitHub issue analysis assistant",
  "docs": "/docs",
  "health": "/health"
}
```

---

### Analyze Issue

Analyze a GitHub issue and get AI-powered insights.

```http
POST /analyze
Content-Type: application/json
```

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo` | string | Yes | Repository in format `owner/repo` |
| `issue_number` | integer | Yes | Issue number to analyze |
| `github_token` | string | No | GitHub PAT for higher rate limits |

#### Example Request

```json
{
  "repo": "vercel/next.js",
  "issue_number": 12345,
  "github_token": "ghp_xxxxxxxxxxxx"
}
```

#### Response

```json
{
  "summary": "This issue reports a hydration mismatch error occurring when using dynamic imports with SSR. Users are seeing console warnings about server/client HTML mismatches. The issue appears when components render differently between server and client due to browser-specific APIs.",
  "root_cause": "The likely root cause is that a component is using browser-specific APIs (like window or localStorage) during server-side rendering, causing the server HTML to differ from the client-rendered HTML.",
  "solution_steps": [
    "Identify the component causing the mismatch by checking console warnings",
    "Wrap browser-specific code in useEffect or check for typeof window",
    "Use dynamic imports with ssr: false for client-only components",
    "Test with SSR disabled to confirm the component is the source"
  ],
  "checklist": [
    "Read and understand the hydration error documentation",
    "Set up a local Next.js development environment",
    "Reproduce the issue with a minimal example",
    "Identify browser-specific API usage in components",
    "Implement proper client-side checks",
    "Test fix with SSR enabled and disabled",
    "Verify no console warnings remain",
    "Submit PR with test case"
  ],
  "labels": ["bug", "enhancement"],
  "similar_issues": [
    {
      "issue_number": 11234,
      "title": "Hydration failed because the initial UI does not match",
      "url": "https://github.com/vercel/next.js/issues/11234",
      "similarity": 0.89
    },
    {
      "issue_number": 10456,
      "title": "SSR mismatch with dynamic content",
      "url": "https://github.com/vercel/next.js/issues/10456",
      "similarity": 0.78
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | 4-6 line summary of the issue |
| `root_cause` | string | AI analysis of likely root cause |
| `solution_steps` | array[string] | Step-by-step fix guidance |
| `checklist` | array[string] | Developer checklist (6-10 items) |
| `labels` | array[string] | Suggested labels |
| `similar_issues` | array[object] | Similar/duplicate issues |

#### Similar Issue Object

| Field | Type | Description |
|-------|------|-------------|
| `issue_number` | integer | Issue number |
| `title` | string | Issue title |
| `url` | string | Issue URL |
| `similarity` | float | Similarity score (0-1) |

#### Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid request (bad repo format, etc.) |
| 404 | Issue not found |
| 500 | Server error (AI failure, etc.) |

```json
{
  "error": "Issue #99999 not found in owner/repo",
  "detail": "The requested issue does not exist or is not accessible"
}
```

---

### Export to Markdown

Export analysis result to formatted markdown.

```http
POST /export
Content-Type: application/json
```

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `analysis` | object | Yes | AnalysisResult from /analyze |

#### Example Request

```json
{
  "analysis": {
    "summary": "Issue summary here...",
    "root_cause": "Root cause analysis...",
    "solution_steps": ["Step 1", "Step 2"],
    "checklist": ["Item 1", "Item 2"],
    "labels": ["bug"],
    "similar_issues": []
  }
}
```

#### Response

```json
{
  "markdown": "# 🔍 Issue Analysis Report\n\n---\n\n## 📋 Summary\n\nIssue summary here...\n\n---\n\n## 🔬 Root Cause Analysis\n\nRoot cause analysis...\n\n---\n\n## 🛠️ Solution Steps\n\n1. Step 1\n2. Step 2\n\n---\n\n## ✅ Developer Checklist\n\n- [ ] Item 1\n- [ ] Item 2\n\n---\n\n## 🏷️ Suggested Labels\n\n`bug`\n\n---\n\n*Generated by [IssuePilot](https://github.com/Scarage1/IssuePilot) 🚀*"
}
```

---

### Check Rate Limit

Check GitHub API rate limit status.

```http
GET /rate-limit?github_token=optional
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `github_token` | string | No | GitHub PAT to check |

#### Response

```json
{
  "limit": 5000,
  "remaining": 4998,
  "reset_at": 1699999999
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": "Error message",
  "detail": "Additional details (optional)"
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limited |
| 500 | Server Error - Internal failure |

---

## Rate Limits

### GitHub API
- **Without token:** 60 requests/hour
- **With token:** 5000 requests/hour

### IssuePilot API
- No built-in rate limiting (self-hosted)
- Consider adding rate limiting in production

---

## Examples

### cURL Commands

```bash
# Health check
curl http://localhost:8000/health

# Analyze an issue
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "facebook/react",
    "issue_number": 12345
  }'

# Analyze with GitHub token (higher rate limits)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "facebook/react",
    "issue_number": 12345,
    "github_token": "ghp_xxxxxxxxxxxx"
  }'

# Check rate limit
curl "http://localhost:8000/rate-limit?github_token=ghp_xxxx"

# Export analysis to markdown
curl -X POST http://localhost:8000/export \
  -H "Content-Type: application/json" \
  -d @analysis.json
```

### Python

```python
import httpx

# Analyze issue
response = httpx.post(
    "http://localhost:8000/analyze",
    json={
        "repo": "facebook/react",
        "issue_number": 12345
    }
)
result = response.json()
print(result["summary"])
```

### JavaScript

```javascript
// Analyze issue
const response = await fetch("http://localhost:8000/analyze", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    repo: "facebook/react",
    issue_number: 12345
  })
});
const result = await response.json();
console.log(result.summary);
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "detail": "Additional details (optional)"
}
```

### 400 Bad Request

Invalid input parameters.

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "invalid-format", "issue_number": 123}'
```

```json
{
  "error": "Invalid repo format. Expected 'owner/repo'",
  "detail": "Repository must be in format 'owner/repository'"
}
```

### 401 Unauthorized

Invalid or expired GitHub token.

```json
{
  "error": "GitHub API authentication failed",
  "detail": "The provided token is invalid or has expired"
}
```

### 404 Not Found

Issue or repository doesn't exist.

```json
{
  "error": "Issue #99999 not found in owner/repo",
  "detail": "The requested issue does not exist or is not accessible"
}
```

### 429 Rate Limited

GitHub API rate limit exceeded.

```json
{
  "error": "GitHub API rate limit exceeded",
  "detail": "Rate limit resets at 2024-01-15T12:00:00Z. Add a GitHub token for higher limits."
}
```

### 500 Server Error

Internal server or AI error.

```json
{
  "error": "AI analysis failed",
  "detail": "OpenAI API returned an error. Please try again."
}
```

---

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request format and parameters |
| 401 | Unauthorized | Verify GitHub token is valid |
| 404 | Not Found | Check repo/issue exists and is public |
| 429 | Rate Limited | Wait or add GitHub token |
| 500 | Server Error | Check logs, retry request |

Interactive API documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Changelog

### v1.0.0
- Initial release
- `/analyze` endpoint
- `/export` endpoint
- `/health` endpoint
- `/rate-limit` endpoint
