# 🚀 IssuePilot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

**AI-powered GitHub issue analysis assistant for open-source maintainers and contributors**

IssuePilot automatically analyzes GitHub issues and provides:
- 📋 **Smart Summaries** - Understand issues in seconds
- 🔬 **Root Cause Analysis** - AI-identified likely causes
- 🛠️ **Solution Plans** - Step-by-step fix guidance
- ✅ **Developer Checklists** - Actionable tasks for contributors
- 🏷️ **Label Suggestions** - Auto-categorization
- 🔗 **Duplicate Detection** - Find similar issues

---

## 📖 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
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
git clone https://github.com/issuepilot/issuepilot.git
cd issuepilot

# Backend setup
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
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
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
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

---

## 🗺️ Roadmap

### v1.0 (MVP) ✅
- [x] Backend + CLI
- [x] AI Summary + checklist
- [x] Export markdown

### v1.5
- [x] Duplicate detection
- [x] Label suggestion

### v2.0
- [ ] GitHub Action integration
- [ ] Dashboard UI
- [ ] PR draft generator

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
