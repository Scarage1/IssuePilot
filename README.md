# 🚀 IssuePilot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://github.com/Scarage1/IssuePilot/actions/workflows/test.yml/badge.svg)](https://github.com/Scarage1/IssuePilot/actions/workflows/test.yml)

**AI-powered GitHub issue analysis assistant for open-source maintainers and contributors**

IssuePilot automatically analyzes GitHub issues and provides:
- 📋 **Smart Summaries** - Understand issues in seconds
- 🔬 **Root Cause Analysis** - AI-identified likely causes
- 🛠️ **Solution Plans** - Step-by-step fix guidance
- ✅ **Developer Checklists** - Actionable tasks for contributors
- 🏷️ **Label Suggestions** - Auto-categorization
- 🔗 **Duplicate Detection** - Find similar issues

---

## 🎯 Project Vision

### The Problem

Open-source maintainers spend **hours** triaging issues:
- Reading long, unstructured bug reports
- Identifying duplicates manually
- Writing the same guidance repeatedly
- Labeling issues inconsistently

Contributors struggle too:
- Understanding complex issues
- Knowing where to start
- Finding related issues

### The Solution

IssuePilot uses AI to **automate issue analysis**, giving maintainers and contributors instant insights. One API call or CLI command transforms a wall of text into actionable intelligence.

### What Makes It Different

| Feature | Traditional | IssuePilot |
|---------|-------------|------------|
| Issue Summary | Manual reading | AI-generated in seconds |
| Root Cause | Guesswork | AI analysis with context |
| Action Items | Write from scratch | Auto-generated checklist |
| Duplicates | Manual search | Automatic similarity detection |
| Labels | Inconsistent | AI-suggested categories |

---

## 📖 Table of Contents

- [Project Vision](#-project-vision)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Examples](#-examples)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [Good First Issues](#-good-first-issues)
- [License](#-license)

---

## ✨ Features

### For Maintainers
- ⏱️ **Reduce triage time** - Get instant issue summaries
- 🏷️ **Auto-label issues** - Consistent categorization
- 💬 **Auto-comment** - Bot posts analysis on new issues

### For Contributors
- 📖 **Understand quickly** - No more reading walls of text
- 📋 **Get checklists** - Know exactly what to do
- 🔍 **Find duplicates** - Avoid working on existing issues

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key
- (Optional) GitHub token for higher rate limits

### 1. Clone & Setup

```bash
git clone https://github.com/Scarage1/IssuePilot.git
cd IssuePilot

# Backend setup
cd backend
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt)
venv\Scripts\activate.bat
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

### 4. Analyze an Issue

```bash
# Using CLI
cd ../cli
pip install -e .
issuepilot analyze --repo facebook/react --issue 12345

# Or using API directly
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo": "facebook/react", "issue_number": 12345}'
```

---

## 📦 Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend (Web UI)

```bash
cd frontend
npm install
npm run dev  # Start development server at http://localhost:3000
```

### CLI Tool

```bash
cd cli
pip install -e .
# Now you can use: issuepilot --help
```

---

## 🔧 Usage

### CLI Commands

```bash
# Analyze an issue
issuepilot analyze --repo vercel/next.js --issue 12345

# Export to markdown
issuepilot analyze --repo vercel/next.js --issue 12345 --export md

# Save to file
issuepilot analyze --repo vercel/next.js --issue 12345 --export md --output analysis.md

# With GitHub token (higher rate limits)
issuepilot analyze --repo vercel/next.js --issue 12345 --token YOUR_TOKEN

# Check API health
issuepilot health
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/analyze` | Analyze a GitHub issue |
| POST | `/export` | Export analysis to markdown |
| GET | `/rate-limit` | Check GitHub API rate limit |

---

## 📚 API Documentation

### Analyze Issue

**POST** `/analyze`

```json
{
  "repo": "owner/repo",
  "issue_number": 12345,
  "github_token": "optional"
}
```

**Response:**

```json
{
  "summary": "Clear summary of the issue...",
  "root_cause": "Analysis of the likely root cause...",
  "solution_steps": [
    "Step 1: Review the affected code",
    "Step 2: Implement the fix",
    "Step 3: Add tests"
  ],
  "checklist": [
    "Read the issue thoroughly",
    "Set up local environment",
    "Reproduce the issue",
    "..."
  ],
  "labels": ["bug", "enhancement"],
  "similar_issues": [
    {
      "issue_number": 12000,
      "title": "Similar issue title",
      "url": "https://github.com/...",
      "similarity": 0.85
    }
  ]
}
```

See [API Documentation](docs/api.md) for complete details.

---

## 📁 Examples

Check out the [examples/](examples/) folder to see IssuePilot in action:

| File | Description |
|------|-------------|
| [example_output.json](examples/example_output.json) | Raw JSON response from the API |
| [example_output.md](examples/example_output.md) | Formatted markdown export |
| [sample_request.json](examples/sample_request.json) | Sample API request payload |

### Sample Output Preview

```json
{
  "summary": "This issue reports a hydration mismatch error...",
  "root_cause": "The component uses browser-specific APIs during SSR...",
  "solution_steps": ["Identify the component...", "Wrap in useEffect..."],
  "checklist": ["Set up local environment", "Reproduce the issue", "..."],
  "labels": ["bug", "ssr", "good-first-issue"],
  "similar_issues": [{"issue_number": 11234, "similarity": 0.89}]
}
```

---

## ⚙️ Configuration

Create a `.env` file in the `backend` directory:

```env
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
GITHUB_TOKEN=your_github_token
AI_PROVIDER=openai
MODEL=gpt-4o-mini
SIMILARITY_THRESHOLD=0.75
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `GITHUB_TOKEN` | No | - | GitHub PAT for higher rate limits |
| `AI_PROVIDER` | No | `openai` | AI provider to use |
| `MODEL` | No | `gpt-4o-mini` | AI model |
| `SIMILARITY_THRESHOLD` | No | `0.75` | Duplicate detection threshold |

See [Configuration Reference](docs/configuration.md) for detailed setup guide and troubleshooting.

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │────▶│   CLI/API   │────▶│   Backend   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
            ┌───────────────┐        ┌───────────────┐        ┌───────────────┐
            │ GitHub Client │        │   AI Engine   │        │   Duplicate   │
            │  (API calls)  │        │   (OpenAI)    │        │    Finder     │
            └───────────────┘        └───────────────┘        └───────────────┘
```

See [Architecture Documentation](docs/architecture.md) for details.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🎨 Improve prompts

### Developer Setup

See [Development Guide](docs/development.md) for:
- Running the backend locally
- Running tests
- Linting and formatting
- Building packages

---

## 🗺️ Roadmap

### v1.0 - Core Features ✅
- [x] FastAPI backend with REST API
- [x] CLI tool for terminal usage
- [x] AI-powered issue summarization
- [x] Root cause analysis
- [x] Developer checklists
- [x] Markdown export

### v1.1 - Enhanced Detection ✅
- [x] Duplicate/similar issue detection
- [x] TF-IDF similarity (offline mode)
- [x] Label suggestions

### v1.2 - Improvements (Next)
- [ ] OpenAI embeddings for better similarity
- [ ] Caching layer for repeated analyses
- [ ] Batch analysis for multiple issues
- [ ] Better error messages and recovery

### v2.0 - Automation
- [ ] GitHub Action for auto-commenting
- [ ] Webhook integration
- [ ] Dashboard UI
- [ ] PR draft generator from issues

### v3.0 - Enterprise
- [ ] Self-hosted LLM support
- [ ] Team analytics
- [ ] Custom prompt templates
- [ ] Multi-repo analysis

---

## 🌱 Good First Issues

Want to contribute but don't know where to start? Here are some beginner-friendly tasks:

| Task | Difficulty | Skills |
|------|------------|--------|
| Improve AI prompts for better summaries | 🟢 Easy | Prompt engineering |
| Add more detailed error messages | 🟢 Easy | Python |
| Add request/response logging | 🟢 Easy | Python, FastAPI |
| Implement response caching | 🟡 Medium | Python, Redis |
| Add support for GitLab issues | 🟡 Medium | Python, APIs |
| Create GitHub Action | 🟡 Medium | GitHub Actions, YAML |
| Add rate limit retry logic | 🟢 Easy | Python, httpx |
| Write more test cases | 🟢 Easy | Python, pytest |
| Add CLI progress spinner | 🟢 Easy | Python, Click |
| Docker containerization | 🟡 Medium | Docker |

Check our [Issues](https://github.com/Scarage1/IssuePilot/issues) page for more!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [OpenAI](https://openai.com/) - AI capabilities
- Open-source community ❤️

---

<p align="center">
  Made with ❤️ by the IssuePilot Team
</p>
