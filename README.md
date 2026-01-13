# IssuePilot

AI-powered GitHub issue analysis tool. Analyze any GitHub issue and get summaries, root cause identification, and implementation steps.

[![Tests](https://github.com/Scarage1/IssuePilot/actions/workflows/test.yml/badge.svg)](https://github.com/Scarage1/IssuePilot/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Features

- **Issue Summary** - Clear, concise summary of the issue
- **Root Cause Analysis** - AI-identified likely causes
- **Implementation Steps** - Actionable guidance to resolve the issue
- **Duplicate Detection** - Find similar issues in the repository
- **Label Suggestions** - Auto-categorization for maintainers
- **Export** - Download analysis as Markdown or JSON

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.9+, FastAPI |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| AI | OpenAI GPT-4 / Google Gemini |
| CLI | Python Click |

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key or Gemini API key

### 1. Clone

```bash
git clone https://github.com/Scarage1/IssuePilot.git
cd IssuePilot
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### 4. CLI (Optional)

```bash
cd cli
pip install -e .
issuepilot analyze --repo owner/repo --issue 123
```

## Docker

```bash
# Copy and configure environment
cp .env.example .env

# Start all services
docker-compose up -d
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Reference

### POST /analyze

Analyze a GitHub issue.

**Request:**
```json
{
  "repo": "facebook/react",
  "issue_number": 12345,
  "github_token": "optional"
}
```

**Response:**
```json
{
  "summary": "Brief description of the issue",
  "root_cause": "Analysis of what's causing the problem",
  "solution_steps": [
    "Step 1: Identify the affected component",
    "Step 2: Implement the fix",
    "Step 3: Add tests"
  ],
  "checklist": [
    "Set up local environment",
    "Reproduce the issue",
    "Submit PR with fix"
  ],
  "labels": ["bug", "good-first-issue"],
  "similar_issues": [
    {
      "issue_number": 11234,
      "title": "Similar issue",
      "similarity": 0.85
    }
  ]
}
```

### GET /health

Health check endpoint.

### GET /rate-limit

Check GitHub API rate limit status.

### POST /export

Export analysis result to Markdown format.

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key |
| `GEMINI_API_KEY` | Yes* | - | Google Gemini API key |
| `AI_PROVIDER` | No | `openai` | AI provider (`openai` or `gemini`) |
| `MODEL` | No | `gpt-4o-mini` | Model to use |
| `GITHUB_TOKEN` | No | - | GitHub PAT for higher rate limits |
| `CACHE_TTL` | No | `3600` | Cache TTL in seconds |

*One of `OPENAI_API_KEY` or `GEMINI_API_KEY` is required.

## Project Structure

```
IssuePilot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # API endpoints
│   │   ├── ai_engine.py    # AI analysis logic
│   │   ├── github_client.py
│   │   ├── duplicate_finder.py
│   │   └── schemas.py
│   └── tests/              # Backend tests
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── hooks/             # Custom hooks
│   └── lib/               # Utilities
├── cli/                   # CLI tool
└── docs/                  # Documentation
```

## Development

### Running Tests

```bash
# Backend (122 tests)
cd backend
pytest

# Frontend (47 tests)
cd frontend
npm test
```

### Linting

```bash
# Backend
cd backend
ruff check .
ruff format .

# Frontend
cd frontend
npm run lint
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Check the [Issues](https://github.com/Scarage1/IssuePilot/issues) page for tasks to work on.

## License

MIT License - see [LICENSE](LICENSE)
