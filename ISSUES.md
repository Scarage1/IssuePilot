# Open Issues

Issues for contributors to work on. Pick one and submit a PR!

---

## Good First Issues

### 1. Add loading spinner to CLI

**Type:** Enhancement  
**Difficulty:** Easy  
**Files:** `cli/issuepilot.py`

The CLI shows a static message during analysis. Add a spinner using `rich` or `halo`.

```python
# Current
print("Analyzing issue...")

# Wanted
with Spinner("Analyzing issue..."):
    result = analyze()
```

---

### 2. Add request logging middleware

**Type:** Enhancement  
**Difficulty:** Easy  
**Files:** `backend/app/main.py`

Log all API requests with method, path, and response time.

```
INFO: POST /analyze - 200 - 2.3s
INFO: GET /health - 200 - 0.1s
```

---

### 3. Improve error messages in AI engine

**Type:** Enhancement  
**Difficulty:** Easy  
**Files:** `backend/app/ai_engine.py`

Add specific error messages for:
- Missing API key
- Rate limit exceeded  
- Invalid model name
- Context too long

---

### 4. Add retry logic for rate limits

**Type:** Enhancement  
**Difficulty:** Easy  
**Files:** `backend/app/github_client.py`

When GitHub API returns 429, retry with exponential backoff.

---

### 5. Cache analysis results

**Type:** Enhancement  
**Difficulty:** Medium  
**Files:** `backend/app/main.py`

Cache results by repo + issue number. Use Redis or in-memory cache.

---

## Features

### 6. Support GitLab issues

**Type:** Feature  
**Difficulty:** Medium  
**Files:** `backend/app/` (new file)

Add a GitLab client similar to `github_client.py`. Parse GitLab issue URLs.

---

### 7. Batch analysis endpoint

**Type:** Feature  
**Difficulty:** Medium  
**Files:** `backend/app/main.py`

Add endpoint to analyze multiple issues at once:

```json
POST /analyze/batch
{
  "issues": [
    {"repo": "owner/repo", "issue_number": 1},
    {"repo": "owner/repo", "issue_number": 2}
  ]
}
```

---

### 8. GitHub Action

**Type:** Feature  
**Difficulty:** Medium  
**Files:** `.github/actions/` (new)

Create a GitHub Action that auto-comments analysis on new issues.

---

### 9. Export to PDF

**Type:** Feature  
**Difficulty:** Medium  
**Files:** `backend/app/main.py`, `frontend/`

Add PDF export option alongside Markdown and JSON.

---

### 10. Dark mode improvements

**Type:** Enhancement  
**Difficulty:** Easy  
**Files:** `frontend/app/globals.css`

Improve dark mode contrast and colors.

---

## Bug Fixes

### 11. Handle private repos gracefully

**Type:** Bug  
**Difficulty:** Easy  
**Files:** `backend/app/github_client.py`

Return clear error when trying to analyze private repo without token.

---

### 12. Fix duplicate detection for short issues

**Type:** Bug  
**Difficulty:** Medium  
**Files:** `backend/app/duplicate_finder.py`

TF-IDF doesn't work well for very short issues. Add minimum content check.

---

## Documentation

### 13. Add API examples

**Type:** Docs  
**Difficulty:** Easy  
**Files:** `docs/api.md`

Add curl examples for all endpoints.

---

### 14. Add deployment guide

**Type:** Docs  
**Difficulty:** Easy  
**Files:** `docs/deployment.md` (new)

Document deploying to:
- Railway
- Vercel
- AWS/GCP

---

## How to Contribute

1. Comment on an issue to claim it
2. Fork the repo
3. Create a branch: `git checkout -b issue-N-description`
4. Make changes
5. Submit PR referencing the issue
