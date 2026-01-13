# Configuration Reference

Complete guide to configuring IssuePilot.

## Environment Variables

IssuePilot is configured via environment variables. Create a `.env` file in the `backend/` directory.

### Quick Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your values
```

---

## Required Variables

### `OPENAI_API_KEY`

Your OpenAI API key for AI-powered analysis.

| Property | Value |
|----------|-------|
| **Required** | Yes |
| **Default** | None |
| **Format** | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

**How to get:**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys
3. Create a new secret key

**Example:**
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Optional Variables

### `GITHUB_TOKEN`

GitHub Personal Access Token for higher API rate limits.

| Property | Value |
|----------|-------|
| **Required** | No |
| **Default** | None (60 requests/hour) |
| **With Token** | 5,000 requests/hour |
| **Format** | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

**How to get:**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select scopes: `repo` (for private repos) or `public_repo` (for public only)

**Example:**
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### `AI_PROVIDER`

The AI provider to use for analysis.

| Property | Value |
|----------|-------|
| **Required** | No |
| **Default** | `openai` |
| **Options** | `openai` |

**Example:**
```env
AI_PROVIDER=openai
```

---

### `MODEL`

The specific AI model to use.

| Property | Value |
|----------|-------|
| **Required** | No |
| **Default** | `gpt-4o-mini` |
| **Options** | `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo` |

**Cost vs Quality:**
| Model | Cost | Quality | Speed |
|-------|------|---------|-------|
| `gpt-3.5-turbo` | $ | Good | Fast |
| `gpt-4o-mini` | $$ | Better | Fast |
| `gpt-4o` | $$$ | Best | Medium |
| `gpt-4-turbo` | $$$$ | Best | Slow |

**Example:**
```env
MODEL=gpt-4o-mini
```

---

### `SIMILARITY_THRESHOLD`

Threshold for duplicate issue detection (0.0 to 1.0).

| Property | Value |
|----------|-------|
| **Required** | No |
| **Default** | `0.75` |
| **Range** | `0.0` - `1.0` |

**Guidelines:**
- `0.9+` - Very strict, only near-exact matches
- `0.75` - Balanced (recommended)
- `0.5` - Loose, may include related issues
- `< 0.5` - Not recommended, too many false positives

**Example:**
```env
SIMILARITY_THRESHOLD=0.75
```

---

### `USE_EMBEDDINGS`

Use OpenAI embeddings for similarity (costs extra API calls).

| Property | Value |
|----------|-------|
| **Required** | No |
| **Default** | `false` |
| **Options** | `true`, `false` |

When `false`, uses TF-IDF (free, offline, fast).
When `true`, uses OpenAI embeddings (more accurate, costs API calls).

**Example:**
```env
USE_EMBEDDINGS=false
```

---

## Complete Example

```env
# Required
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional - GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional - AI Settings
AI_PROVIDER=openai
MODEL=gpt-4o-mini

# Optional - Duplicate Detection
SIMILARITY_THRESHOLD=0.75
USE_EMBEDDINGS=false
```

---

## Troubleshooting

### "Invalid API Key" Error

**Symptoms:**
```
Error: Invalid API key provided
```

**Solutions:**
1. Check for typos in your API key
2. Ensure no extra spaces or newlines
3. Verify the key is active at [platform.openai.com](https://platform.openai.com)
4. Try regenerating the key

---

### GitHub Rate Limit Errors

**Symptoms:**
```
Error: API rate limit exceeded
```

**Solutions:**
1. Add a `GITHUB_TOKEN` to increase limits from 60 to 5,000/hour
2. Wait for the rate limit to reset (usually 1 hour)
3. Check current limits: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit`

---

### OpenAI Rate Limit Errors

**Symptoms:**
```
Error: Rate limit reached for requests
```

**Solutions:**
1. Wait a few seconds and retry
2. Upgrade your OpenAI plan for higher limits
3. Use a less expensive model (`gpt-3.5-turbo`)
4. Add retry logic in your application

---

### Model Not Found Error

**Symptoms:**
```
Error: The model 'gpt-4' does not exist
```

**Solutions:**
1. Use `gpt-4o-mini` (available to all accounts)
2. Check if your OpenAI account has GPT-4 access
3. Verify model name spelling

---

## Security Best Practices

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use environment-specific keys** - Different keys for dev/prod
3. **Rotate keys periodically** - Regenerate every 90 days
4. **Use minimal scopes** - GitHub token only needs `public_repo`
5. **Set spending limits** - Configure in OpenAI dashboard

---

## CLI Configuration

The CLI can also use environment variables or command-line arguments:

```bash
# Using environment variables
export OPENAI_API_KEY=sk-xxx
export GITHUB_TOKEN=ghp-xxx
issuepilot analyze --repo owner/repo --issue 123

# Using command-line arguments
issuepilot analyze --repo owner/repo --issue 123 --token ghp-xxx
```

**Priority order:**
1. Command-line arguments (highest)
2. Environment variables
3. `.env` file
4. Default values (lowest)
