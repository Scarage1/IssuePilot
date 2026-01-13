# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### GET /health

Health check.

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok"}
```

### GET /rate-limit

Check GitHub API rate limit status.

```bash
curl http://localhost:8000/rate-limit
```

```json
{
  "limit": 60,
  "remaining": 58,
  "reset_at": "2024-01-15T10:30:00Z"
}
```

### POST /analyze

Analyze a GitHub issue.

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "facebook/react", "issue_number": 12345}'
```

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| repo | string | Yes | `owner/repo` format |
| issue_number | integer | Yes | Issue number |
| github_token | string | No | GitHub PAT for private repos |

**Response:**

```json
{
  "summary": "Brief summary of the issue",
  "root_cause": "Analysis of the likely cause",
  "solution_steps": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "checklist": [
    "Task 1",
    "Task 2"
  ],
  "labels": ["bug", "enhancement"],
  "similar_issues": [
    {
      "issue_number": 11234,
      "title": "Related issue",
      "url": "https://github.com/...",
      "similarity": 0.85
    }
  ]
}
```

### POST /export

Export analysis to Markdown.

```bash
curl -X POST http://localhost:8000/export \
  -H "Content-Type: application/json" \
  -d '{"summary": "...", "root_cause": "...", ...}'
```

Returns Markdown text.

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Invalid request |
| 404 | Issue not found |
| 429 | Rate limit exceeded |
| 500 | Server error |

```json
{
  "detail": "Error message"
}
```
