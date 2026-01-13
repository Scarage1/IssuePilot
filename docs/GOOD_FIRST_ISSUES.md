# 🌱 Good First Issues for IssuePilot

This document contains 10 beginner-friendly issues for new contributors to IssuePilot. Each issue is labeled with `good first issue` and `enhancement`.

---

## Issue 1: Add CLI Progress Spinner During Analysis

**Title:** Add CLI progress spinner during issue analysis

**Labels:** `good first issue`, `enhancement`

**Description:**

Currently, when running `issuepilot analyze`, users see a static message while waiting for the analysis to complete. This can take several seconds, leaving users uncertain about the progress.

**Goal:**
Add a progress spinner or animation to the CLI to provide visual feedback during the analysis process.

**Suggested Implementation:**
- Use a library like `rich` or `halo` for the spinner
- Show spinner while waiting for API response
- Display elapsed time or progress stages

**Files to Modify:**
- `cli/issuepilot.py`

**Acceptance Criteria:**
- [ ] Spinner appears when analysis starts
- [ ] Spinner stops when analysis completes
- [ ] Works on Windows, macOS, and Linux terminals

**Resources:**
- [rich library](https://github.com/Textualize/rich)
- [halo library](https://github.com/manrajgrover/halo)

---

## Issue 2: Add Request/Response Logging to Backend

**Title:** Add configurable request/response logging to the backend API

**Labels:** `good first issue`, `enhancement`

**Description:**

The backend currently lacks structured logging for API requests and responses. This makes debugging and monitoring difficult in production environments.

**Goal:**
Implement request/response logging using Python's logging module or a library like `loguru`.

**Suggested Implementation:**
- Add middleware to log incoming requests (method, path, timing)
- Log responses with status codes
- Make logging level configurable via environment variable

**Files to Modify:**
- `backend/app/main.py`
- `backend/.env.example` (add LOG_LEVEL variable)

**Acceptance Criteria:**
- [ ] All API requests are logged with timestamp, method, and path
- [ ] Response status codes and timing are logged
- [ ] Log level is configurable (DEBUG, INFO, WARNING, ERROR)
- [ ] Sensitive data (tokens) is not logged

---

## Issue 3: Improve Error Messages in AI Engine

**Title:** Add more descriptive error messages in AI engine

**Labels:** `good first issue`, `enhancement`

**Description:**

When AI analysis fails, the error messages are often generic and unhelpful for troubleshooting. Users need better guidance on what went wrong and how to fix it.

**Goal:**
Improve error handling and messages in the AI engine to provide actionable guidance.

**Suggested Implementation:**
- Check for missing or invalid API key and provide specific message
- Handle rate limit errors with retry suggestions
- Handle model-specific errors (e.g., context length exceeded)

**Files to Modify:**
- `backend/app/ai_engine.py`

**Acceptance Criteria:**
- [ ] Missing API key shows: "OpenAI API key not configured. Set OPENAI_API_KEY in .env"
- [ ] Rate limit error shows: "OpenAI rate limit reached. Please wait and try again."
- [ ] Invalid model shows list of valid models
- [ ] All error messages include actionable next steps

---

## Issue 4: Add Rate Limit Retry Logic

**Title:** Implement automatic retry logic for GitHub API rate limits

**Labels:** `good first issue`, `enhancement`

**Description:**

When the GitHub API rate limit is exceeded, the application fails immediately. Users must manually wait and retry, which is a poor experience.

**Goal:**
Implement automatic retry logic with exponential backoff when GitHub rate limits are hit.

**Suggested Implementation:**
- Detect 403 rate limit response from GitHub
- Implement exponential backoff (e.g., 1s, 2s, 4s)
- Allow configurable max retries (default: 3)
- Log retry attempts

**Files to Modify:**
- `backend/app/github_client.py`

**Acceptance Criteria:**
- [ ] Automatically retries on rate limit errors
- [ ] Uses exponential backoff between retries
- [ ] Max retries is configurable
- [ ] Logs each retry attempt
- [ ] Fails gracefully after max retries with clear error message

---

## Issue 5: Write Additional Test Cases for Utils Module

**Title:** Increase test coverage for utils module

**Labels:** `good first issue`, `enhancement`

**Description:**

The `backend/app/utils.py` module has limited test coverage. Adding more test cases will improve reliability and help catch edge cases.

**Goal:**
Add comprehensive test cases for the markdown export functionality and any utility functions.

**Suggested Implementation:**
- Test markdown export with various input combinations
- Test edge cases (empty fields, special characters, long text)
- Test Unicode handling
- Aim for >90% coverage of utils.py

**Files to Modify:**
- `backend/tests/test_utils.py`

**Acceptance Criteria:**
- [ ] Tests cover all functions in utils.py
- [ ] Edge cases are tested (empty input, None values, special chars)
- [ ] Tests pass on CI
- [ ] Coverage of utils.py is >90%

---

## Issue 6: Add JSON Schema Validation for API Requests

**Title:** Add JSON schema validation for API request payloads

**Labels:** `good first issue`, `enhancement`

**Description:**

The API currently relies on Pydantic for validation, but could benefit from additional schema documentation and validation. Better validation helps users understand expected inputs.

**Goal:**
Enhance request validation with clear error messages for invalid inputs.

**Suggested Implementation:**
- Add validation for repository format (owner/repo)
- Validate issue number is positive
- Return detailed validation errors with field names

**Files to Modify:**
- `backend/app/schemas.py`

**Acceptance Criteria:**
- [ ] Invalid repo format returns: "Repository must be in format 'owner/repo'"
- [ ] Negative issue numbers are rejected with clear message
- [ ] Empty repo name is rejected
- [ ] All validation errors include the field name

---

## Issue 7: Add Health Check Endpoint Details

**Title:** Enhance health check endpoint with dependency status

**Labels:** `good first issue`, `enhancement`

**Description:**

The current `/health` endpoint only returns `{"status": "ok"}`. For production monitoring, it would be helpful to include the status of dependencies.

**Goal:**
Enhance the health check to report the status of external dependencies (GitHub API, OpenAI API).

**Suggested Implementation:**
- Check if OpenAI API key is configured
- Optionally ping GitHub API to verify connectivity
- Return structured status for each dependency

**Files to Modify:**
- `backend/app/main.py`
- `backend/app/schemas.py` (update HealthResponse)

**Example Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "dependencies": {
    "openai_api_configured": true,
    "github_api_accessible": true
  }
}
```

**Acceptance Criteria:**
- [ ] Health endpoint includes version number
- [ ] Shows OpenAI API key configuration status
- [ ] Optionally checks GitHub API accessibility
- [ ] Response schema is documented

---

## Issue 8: Add CLI Configuration File Support

**Title:** Support configuration file for CLI settings

**Labels:** `good first issue`, `enhancement`

**Description:**

Currently, CLI users must specify the API URL and token via command-line arguments or environment variables each time. A configuration file would improve usability.

**Goal:**
Add support for a `.issuepilotrc` or `config.yaml` configuration file.

**Suggested Implementation:**
- Look for config file in home directory (`~/.issuepilotrc`)
- Support YAML or JSON format
- Allow settings: api_url, github_token, default_export_format
- Command-line args should override config file

**Files to Modify:**
- `cli/issuepilot.py`

**Example Config File:**
```yaml
api_url: http://localhost:8000
github_token: ghp_xxxxx
default_export_format: md
```

**Acceptance Criteria:**
- [ ] CLI reads config from `~/.issuepilotrc` if present
- [ ] Supports both YAML and JSON formats
- [ ] Command-line arguments override config file settings
- [ ] Missing config file is handled gracefully

---

## Issue 9: Add API Response Caching

**Title:** Implement caching for repeated issue analyses

**Labels:** `good first issue`, `enhancement`

**Description:**

Analyzing the same issue multiple times makes redundant API calls to both GitHub and OpenAI, wasting resources and time. A caching layer would improve performance.

**Goal:**
Implement in-memory caching for issue analyses with configurable TTL.

**Suggested Implementation:**
- Use `cachetools` or simple dict-based cache
- Cache key: `{repo}:{issue_number}`
- Configurable TTL (default: 5 minutes)
- Add optional `--no-cache` flag to CLI

**Files to Modify:**
- `backend/app/main.py`
- `cli/issuepilot.py`

**Acceptance Criteria:**
- [ ] Repeated analysis of same issue returns cached result
- [ ] Cache has configurable TTL
- [ ] CLI has `--no-cache` option to bypass cache
- [ ] Cache is cleared on server restart

---

## Issue 10: Add Dockerfile for Easy Deployment

**Title:** Add Dockerfile and docker-compose for containerized deployment

**Labels:** `good first issue`, `enhancement`

**Description:**

Currently, users must manually set up Python, install dependencies, and configure the environment. A Docker setup would simplify deployment significantly.

**Goal:**
Create a Dockerfile and docker-compose.yml for easy containerized deployment.

**Suggested Implementation:**
- Create multi-stage Dockerfile (build + runtime)
- Use Python 3.11 slim base image
- Create docker-compose.yml for local development
- Document Docker usage in README

**Files to Create:**
- `Dockerfile`
- `docker-compose.yml`
- Update `README.md` with Docker instructions

**Example docker-compose.yml:**
```yaml
version: '3.8'
services:
  issuepilot:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
```

**Acceptance Criteria:**
- [ ] `docker build` creates working image
- [ ] `docker-compose up` starts the service
- [ ] Environment variables can be passed via .env file
- [ ] Image size is optimized (<500MB)
- [ ] README includes Docker setup instructions

---

## How to Create These Issues

To create these issues in the GitHub repository:

1. Go to your repository's Issues page and click "New issue"
2. Copy the **Title** for each issue
3. Copy the **Description** section (everything between the title and the next issue)
4. Add the labels: `good first issue` and `enhancement`
5. Click "Submit new issue"

Alternatively, use the GitHub CLI:
```bash
gh issue create --title "Issue title" --body "Issue body" --label "good first issue" --label "enhancement"
```

---

## Contributing

If you're interested in working on any of these issues:

1. Comment on the issue to let maintainers know you're working on it
2. Read [CONTRIBUTING.md](/CONTRIBUTING.md) for guidelines
3. Create a branch: `git checkout -b feature/issue-name`
4. Make your changes and submit a PR

Happy contributing! 🎉
