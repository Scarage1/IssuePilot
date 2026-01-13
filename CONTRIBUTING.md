# Contributing to IssuePilot

Thanks for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/IssuePilot.git`
3. Create a branch: `git checkout -b feature/your-feature`

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running Tests

```bash
# Backend
cd backend
pytest

# Frontend  
cd frontend
npm test
```

## Code Style

### Python (Backend)

- Use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Run `ruff check .` and `ruff format .` before committing

### TypeScript (Frontend)

- Use ESLint and Prettier
- Run `npm run lint` before committing

## Pull Request Process

1. Ensure tests pass
2. Update documentation if needed
3. Use clear commit messages
4. Reference any related issues

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add caching for API responses
fix: handle rate limit errors gracefully
docs: update API documentation
test: add tests for duplicate finder
```

## Questions?

Open an issue or start a discussion.
