# Contributing to IssuePilot

First off, thank you for considering contributing to IssuePilot! 🎉

It's people like you that make IssuePilot such a great tool for the open-source community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please be respectful and inclusive.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account
- OpenAI API key (for testing AI features)

### Fork & Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR-USERNAME/issuepilot.git
cd issuepilot
```

3. Add the upstream remote:

```bash
git remote add upstream https://github.com/Scarage1/IssuePilot.git
```

---

## 🤔 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

When creating a bug report, include:
- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable

### 💡 Suggesting Features

Feature requests are welcome! Please provide:
- **Clear description** of the feature
- **Use case** - why is this feature needed?
- **Possible implementation** ideas (optional)

### 📝 Improving Documentation

Documentation improvements are always appreciated:
- Fix typos or unclear explanations
- Add examples
- Improve API documentation
- Translate documentation

### 🔧 Code Contributions

#### Good First Issues

Look for issues labeled `good-first-issue` - these are great for newcomers!

#### Areas to Contribute

- **Prompts** - Improve AI prompts for better analysis
- **Duplicate Detection** - Better similarity algorithms
- **GitHub Action** - Implement the action integration
- **Caching** - Add caching for better performance
- **Tests** - Improve test coverage

---

## 🛠️ Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn app.main:app --reload
```

### CLI Setup

```bash
cd cli
pip install -e .
```

### Running Tests

```bash
cd backend
pytest --cov=app tests/
```

---

## 📥 Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Add tests for new features
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run tests
pytest

# Check code style
black --check .
isort --check-only .
ruff check .
```

### 4. Commit Your Changes

Write clear commit messages:

```bash
git commit -m "feat: add duplicate detection threshold config"
# or
git commit -m "fix: handle empty issue body gracefully"
# or
git commit -m "docs: improve API documentation"
```

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

### 6. PR Requirements

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated (if needed)
- [ ] PR description explains changes

---

## 🎨 Style Guidelines

### Python

We follow PEP 8 with these tools:
- **Black** - Code formatting
- **isort** - Import sorting
- **ruff** - Linting

Run before committing:

```bash
black .
isort .
ruff check . --fix
```

### Code Style

```python
# Good
def analyze_issue(repo: str, issue_number: int) -> AnalysisResult:
    """
    Analyze a GitHub issue.
    
    Args:
        repo: Repository in format 'owner/repo'
        issue_number: Issue number to analyze
        
    Returns:
        AnalysisResult with structured analysis
    """
    pass

# Type hints are required
# Docstrings are required for public functions
# Keep functions focused and small
```

### Documentation

- Use clear, concise language
- Include code examples
- Keep README up to date

---

## ❓ Questions?

Feel free to open an issue with the `question` label or start a discussion.

---

## 🙏 Thank You!

Your contributions make IssuePilot better for everyone. We appreciate your time and effort!

---

<p align="center">
  Happy Contributing! 🚀
</p>
