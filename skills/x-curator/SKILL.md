---
name: x-curator
description: Curate X (Twitter) links sent by the user — fetch real tweet content via the X API, evaluate signal vs. noise, archive to a daily markdown log, follow the author, and optionally implement insights. Use when the user sends an X/Twitter URL and wants it read, evaluated, and saved. Never guess tweet content — always fetch first. Triggers on any x.com or twitter.com link.
---

# X Curator

Fetch, evaluate, archive, and act on X/Twitter links.

## Setup

### Credentials (save to `~/.openclaw/workspace/.secrets/`)
- `x_bearer_token` — read-only tweet fetching (required)
- `x_api_key` + `x_api_secret` — OAuth 1.0a app credentials (required for following)
- `x_access_token` + `x_access_secret` — OAuth 1.0a user credentials (required for following)

### First-time setup
```bash
mkdir -p ~/.openclaw/workspace/.secrets ~/.openclaw/workspace/links
echo "YOUR_BEARER_TOKEN" > ~/.openclaw/workspace/.secrets/x_bearer_token
echo "YOUR_API_KEY"      > ~/.openclaw/workspace/.secrets/x_api_key
echo "YOUR_API_SECRET"   > ~/.openclaw/workspace/.secrets/x_api_secret
echo "YOUR_ACCESS_TOKEN" > ~/.openclaw/workspace/.secrets/x_access_token
echo "YOUR_ACCESS_SECRET"> ~/.openclaw/workspace/.secrets/x_access_secret
```

Get credentials at: developer.x.com → your app → Keys and Tokens

---

## Workflow

When the user sends an X/Twitter URL:

### 1. Fetch (always first)
```bash
python3 <skill-dir>/scripts/fetch-tweet.py <url>
```
Fetch order: X API v2 → oEmbed → nitter mirrors → FAIL (refuse to proceed without real content)

### 2. Evaluate
**Keep if:** concrete insight, trading edge, actionable self-improvement, useful tool/technique, non-obvious idea
**Skip if:** hot take, motivational fluff, obvious content, hype/drama

### 3. If keeping — run full pipeline
```bash
python3 <skill-dir>/scripts/fetch-tweet.py <url> --tag <tag> --follow
```

Tags: `trading` | `self-improvement` | `tool` | `crypto` | `other`

This archives to `~/.openclaw/workspace/links/YYYY-MM-DD.md` and follows the author.

### 4. If the tweet contains actionable insights
Write key takeaways to `memory/YYYY-MM-DD.md`. Update `MEMORY.md` if significant.

### 5. If skipping
Tell the user why in one sentence. Don't silently skip.

---

## Reading the Archive
```bash
# Today's links
cat ~/.openclaw/workspace/links/$(date +%Y-%m-%d).md

# Search all
grep -r "keyword" ~/.openclaw/workspace/links/

# By tag
grep -r "#trading" ~/.openclaw/workspace/links/
```

---

## Script Reference
`scripts/fetch-tweet.py <url> [--tag TAG] [--follow] [--note "text"]`

- `--tag` — category tag (default: other)
- `--follow` — follow the tweet author via OAuth 1.0a
- `--note` — append a note to the archive entry
