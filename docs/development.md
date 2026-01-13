# Developer Setup Guide

Complete guide for contributors to set up their development environment.

## Prerequisites

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)
- **OpenAI API Key** - [Get one](https://platform.openai.com/api-keys)

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Scarage1/IssuePilot.git
cd IssuePilot

# 2. Set up backend
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 4. Run the server
uvicorn app.main:app --reload
```

---

## Project Structure

```
IssuePilot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # API routes
│   │   ├── schemas.py       # Pydantic models
│   │   ├── github_client.py # GitHub API client
│   │   ├── ai_engine.py     # OpenAI integration
│   │   ├── duplicate_finder.py
│   │   └── utils.py
│   ├── tests/               # Test suite
│   ├── requirements.txt
│   └── .env.example
├── cli/                     # Command-line tool
│   ├── issuepilot.py
│   └── setup.py
├── docs/                    # Documentation
├── examples/                # Sample outputs
└── .github/workflows/       # CI/CD
```

---

## Running the Backend

### Development Server

```bash
cd backend

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Running the CLI

### Install in Development Mode

```bash
cd cli
pip install -e .
```

### Usage

```bash
# Check installation
issuepilot --version

# Analyze an issue
issuepilot analyze --repo facebook/react --issue 12345

# Check health
issuepilot health

# Export to markdown
issuepilot analyze --repo vercel/next.js --issue 1234 --export md
```

---

## Running Tests

### Full Test Suite

```bash
cd backend

# Activate virtual environment first
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Open coverage report
# Windows:
start htmlcov/index.html
# macOS:
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Single test file
pytest tests/test_api.py -v

# Single test class
pytest tests/test_api.py::TestHealthEndpoint -v

# Single test function
pytest tests/test_api.py::TestHealthEndpoint::test_health_check -v

# Tests matching pattern
pytest tests/ -v -k "duplicate"
```

### Test with Markers

```bash
# Skip slow tests
pytest tests/ -v -m "not slow"

# Run only async tests
pytest tests/ -v -m "asyncio"
```

---

## Linting & Formatting

### Check Code Style

```bash
cd backend

# Run ruff (linter)
python -m ruff check app/

# Run black (formatter check)
python -m black --check app/

# Run isort (import sorter check)
python -m isort --check-only --profile black app/

# Run all checks
python -m ruff check app/ && python -m black --check app/ && python -m isort --check-only --profile black app/
```

### Auto-fix Issues

```bash
cd backend

# Format code with black
python -m black app/

# Sort imports with isort
python -m isort --profile black app/

# Auto-fix ruff issues
python -m ruff check app/ --fix
```

### Pre-commit Hook (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Building Packages

### CLI Package

```bash
cd cli

# Build distribution
pip install build
python -m build

# Output in dist/
# - issuepilot-1.0.0.tar.gz
# - issuepilot-1.0.0-py3-none-any.whl
```

### Install Locally

```bash
# From wheel
pip install dist/issuepilot-1.0.0-py3-none-any.whl

# From source
pip install -e .
```

---

## Environment Setup

### VS Code (Recommended)

1. Install extensions:
   - Python
   - Pylance
   - Black Formatter
   - Ruff

2. Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "python.analysis.typeCheckingMode": "basic"
}
```

### PyCharm

1. Set interpreter: `backend/venv/Scripts/python.exe`
2. Enable Black formatter
3. Enable pytest as test runner

---

## Common Development Tasks

### Adding a New Endpoint

1. Define schema in `backend/app/schemas.py`
2. Add route in `backend/app/main.py`
3. Add tests in `backend/tests/test_api.py`
4. Update `docs/api.md`

### Adding a New CLI Command

1. Add command in `cli/issuepilot.py`
2. Update `cli/setup.py` if needed
3. Update `README.md` usage section

### Modifying AI Prompts

1. Edit prompts in `backend/app/ai_engine.py`
2. Test with various issues
3. Update tests if output format changes

---

## Debugging

### VS Code Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env"
    },
    {
      "name": "CLI",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/cli/issuepilot.py",
      "args": ["analyze", "--repo", "facebook/react", "--issue", "1"],
      "cwd": "${workspaceFolder}/cli"
    },
    {
      "name": "Tests",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

### Debugging Tips

1. **API Issues**: Check `/docs` for Swagger UI
2. **Rate Limits**: Use `GET /rate-limit` to check GitHub limits
3. **AI Responses**: Check logs for full prompts/responses
4. **Test Failures**: Run with `-v --tb=long` for details

---

## Troubleshooting

### Virtual Environment Issues

```bash
# Recreate venv
rm -rf venv  # or: rmdir /s /q venv (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Import Errors

```bash
# Ensure you're in the right directory
cd backend

# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Test Failures

```bash
# Run with verbose output
pytest tests/ -v --tb=long

# Check for async issues
pytest tests/ -v --asyncio-mode=auto
```

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/Scarage1/IssuePilot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Scarage1/IssuePilot/discussions)
- **Email**: Create an issue for support

Happy coding! 🚀
