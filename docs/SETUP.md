# Setup Guide

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Required (one of these)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Optional
AI_PROVIDER=openai          # or gemini
MODEL=gpt-4o-mini           # or gemini-1.5-flash
GITHUB_TOKEN=ghp_...        # for higher rate limits
CACHE_TTL=3600              # cache duration in seconds
MAX_CACHE_SIZE=1000         # max cached items
SIMILARITY_THRESHOLD=0.75   # duplicate detection threshold
```

## Getting API Keys

### OpenAI

1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `OPENAI_API_KEY`

### Google Gemini

1. Go to https://aistudio.google.com/apikey
2. Create API key
3. Copy to `GEMINI_API_KEY`

### GitHub Token (Optional)

1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `repo` scope for private repos
4. Copy to `GITHUB_TOKEN`

## Models

### OpenAI Models

| Model | Cost | Quality |
|-------|------|---------|
| gpt-4o-mini | Low | Good |
| gpt-4o | Medium | Better |
| gpt-4-turbo | High | Best |

### Gemini Models

| Model | Cost | Quality |
|-------|------|---------|
| gemini-1.5-flash | Free tier | Good |
| gemini-1.5-pro | Paid | Better |

## Rate Limits

### GitHub API

- Without token: 60 requests/hour
- With token: 5,000 requests/hour

### OpenAI API

- Depends on your plan
- Check https://platform.openai.com/usage

### Gemini API

- Free tier: 15 requests/minute
- Check https://ai.google.dev/pricing
