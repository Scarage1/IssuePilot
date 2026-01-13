# IssuePilot Architecture

This document describes the architecture and design decisions for IssuePilot.

## Overview

IssuePilot is designed as a modular, extensible system for analyzing GitHub issues using AI.

## How It Works - Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              IssuePilot Analysis Flow                                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
  │  User    │────▶│ CLI/API  │────▶│ GitHub API   │────▶│ Issue Data   │────▶│  Prompt  │
  │ Request  │     │ Endpoint │     │ Fetch        │     │ + Comments   │     │ Builder  │
  └──────────┘     └──────────┘     └──────────────┘     └──────────────┘     └────┬─────┘
                                                                                    │
                                                                                    ▼
  ┌──────────┐     ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
  │  Output  │◀────│ Markdown │◀────│ Duplicate    │◀────│    JSON      │◀────│   LLM    │
  │  (JSON/  │     │ Generator│     │ Finder       │     │  Validator   │     │ (OpenAI) │
  │   MD)    │     │          │     │ (TF-IDF)     │     │              │     │          │
  └──────────┘     └──────────┘     └──────────────┘     └──────────────┘     └──────────┘
```

### Step-by-Step Flow

1. **User Request** → User submits repo + issue number via CLI or API
2. **CLI/API Endpoint** → FastAPI receives and validates the request
3. **GitHub API Fetch** → Fetches issue details, comments, and open issues
4. **Issue Data** → Structures the raw data for analysis
5. **Prompt Builder** → Constructs optimized prompt with issue context
6. **LLM (OpenAI)** → AI generates analysis (summary, root cause, steps)
7. **JSON Validator** → Validates and cleans the AI response
8. **Duplicate Finder** → Compares against open issues using TF-IDF
9. **Markdown Generator** → Formats output if export requested
10. **Output** → Returns JSON response or markdown file

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              IssuePilot System                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│  │   CLI Tool   │    │   Web API    │    │   GitHub Action (Planned)    │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┬───────────────┘  │
│         │                   │                           │                   │
│         └───────────────────┴───────────────────────────┘                   │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        FastAPI Backend                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Schemas   │  │   Utils     │  │   Routes    │  │  Middleware │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                           │
│         ▼                   ▼                   ▼                           │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   GitHub    │     │     AI      │     │  Duplicate  │                   │
│  │   Client    │     │   Engine    │     │   Finder    │                   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │ GitHub API  │     │  OpenAI API │     │ Embeddings/ │                   │
│  │             │     │             │     │   TF-IDF    │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. FastAPI Backend (`backend/app/`)

The core server that handles all API requests.

#### main.py
- Application entry point
- Route definitions
- Middleware configuration
- CORS settings

#### schemas.py
- Pydantic models for request/response validation
- `AnalyzeRequest` - Input for analysis
- `AnalysisResult` - Output structure
- `GitHubIssue` - Issue data model

#### github_client.py
- GitHub API interactions
- Fetches issue details, comments
- Retrieves open issues for duplicate detection
- Rate limit handling

#### ai_engine.py
- AI/LLM interactions
- Prompt management
- Response parsing and validation
- Supports OpenAI models

#### duplicate_finder.py
- Similarity detection
- Embeddings-based approach (OpenAI)
- TF-IDF fallback for offline mode
- Configurable threshold

#### utils.py
- Helper functions
- Text processing
- Markdown generation
- Input validation

---

### 2. CLI Tool (`cli/`)

Command-line interface for direct usage.

#### issuepilot.py
- Argument parsing
- API client
- Output formatting
- Export functionality

---

### 3. GitHub Action (Planned)

Automated bot for commenting on new issues.

```yaml
# Trigger: on issue opened
# Action: 
#   1. Fetch issue data
#   2. Call IssuePilot API
#   3. Post comment with analysis
```

---

## Data Flow

### Analyze Issue Flow

```
1. User Request
   └─▶ CLI/API receives repo + issue_number

2. Fetch Issue
   └─▶ GitHub Client fetches issue details
       └─▶ Title, body, comments, labels

3. AI Analysis
   └─▶ AI Engine processes issue
       └─▶ Generates summary, root cause, steps

4. Duplicate Detection
   └─▶ Fetch open issues from repo
       └─▶ Compare embeddings/TF-IDF
       └─▶ Return similar issues

5. Response
   └─▶ Combine results
       └─▶ Return structured AnalysisResult
```

---

## AI Prompt Design

### System Prompt
```
You are a senior open-source maintainer...
```

### User Prompt Structure
```
Issue Title: {title}
Issue Body: {body}
Top Comments: {comments}

Task:
1. Summarize...
2. Root cause...
3. Solution steps...
4. Checklist...
5. Labels...
```

### Output Format
```json
{
  "summary": "...",
  "root_cause": "...",
  "solution_steps": [...],
  "checklist": [...],
  "labels": [...]
}
```

---

## Duplicate Detection

### Approach A: Embeddings (Recommended)

```
1. Create embedding of target issue (title + body)
2. Fetch and embed open issues
3. Compute cosine similarity
4. Return matches above threshold (0.75)
```

**Pros:**
- Semantic understanding
- Better for different wording

**Cons:**
- Requires API calls
- Cost per request

### Approach B: TF-IDF (Offline)

```
1. Vectorize issue texts
2. Compute TF-IDF matrix
3. Calculate cosine similarity
4. Return top matches
```

**Pros:**
- No external API needed
- Fast and free

**Cons:**
- Keyword-based only
- May miss semantic matches

---

## Security Considerations

### API Keys
- Never stored in code
- Loaded from environment variables
- Optional GitHub token support

### Input Validation
- Pydantic schema validation
- Repository format validation (`owner/repo`)
- Input sanitization (remove null bytes, limit length)

### Rate Limiting
- GitHub API rate awareness
- Encourage token usage for higher limits

---

## Scalability

### Current Design
- Stateless API
- Single-process deployment

### Future Improvements
- Redis caching for embeddings
- PostgreSQL for issue history
- Worker queues for batch processing
- Horizontal scaling with load balancer

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | FastAPI | Web framework |
| Validation | Pydantic | Schema validation |
| HTTP Client | httpx | Async HTTP requests |
| AI | OpenAI | LLM for analysis |
| ML | scikit-learn | TF-IDF similarity |
| CLI | argparse | Command-line interface |

---

## Deployment

### Local Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Planned)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

## Future Architecture

### v2.0 Plans

```
                    ┌─────────────────┐
                    │   Dashboard UI  │
                    │    (React/Vue)  │
                    └────────┬────────┘
                             │
┌────────────┐      ┌────────▼────────┐      ┌────────────┐
│   GitHub   │──────│   API Gateway   │──────│   Redis    │
│   Action   │      │    (FastAPI)    │      │   Cache    │
└────────────┘      └────────┬────────┘      └────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐
       │   Worker    │ │   Worker  │ │   Worker  │
       │   Queue     │ │   Queue   │ │   Queue   │
       └─────────────┘ └───────────┘ └───────────┘
```

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [scikit-learn TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
