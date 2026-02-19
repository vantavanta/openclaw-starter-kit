# X-Research Skill Setup

**Purpose:** Search and analyze X/Twitter for real-time perspectives, dev discussions, and expert opinions.

---

## Prerequisites

1. **X API Developer Account**
   - Sign up at: https://developer.x.com
   - Create a project and app
   - Generate API credentials

2. **Python dependencies:**
   ```bash
   pip install requests python-dotenv
   ```

---

## Installation

1. **Copy skill to your workspace:**
   ```bash
   cp -r skills/x-research ~/.openclaw/workspace/skills/
   ```

2. **Create credentials file:**
   ```bash
   cat > ~/.openclaw/x-api-credentials.json << 'JSON'
   {
     "apiKey": "YOUR_API_KEY",
     "apiSecret": "YOUR_API_SECRET",
     "bearerToken": "YOUR_BEARER_TOKEN"
   }
   JSON
   ```

3. **Get your credentials from X Developer Portal:**
   - API Key: Your app's consumer key
   - API Secret: Your app's consumer secret
   - Bearer Token: Generate in "Keys and tokens" section

4. **Test the skill:**
   ```bash
   cd ~/.openclaw/workspace/skills/x-research
   python3 scripts/fetch_tweet.py "TWEET_ID"
   ```

---

## Usage

**The skill activates automatically when you:**
- Say "x research [topic]"
- Say "search x for [topic]"
- Say "what are people saying about [topic]"
- Say "check x for [topic]"

**Or manually run scripts:**
```bash
# Fetch a single tweet
python3 scripts/fetch_tweet.py "TWEET_ID"

# Fetch a thread
python3 scripts/fetch_thread.py "CONVERSATION_ID"

# Search recent (last 7 days)
python3 scripts/search_recent.py "query string" --max-results 50
```

---

## Limitations

**Recent search endpoint:**
- Only indexes last **7 days** of tweets
- For older content, use direct tweet fetch (scripts/fetch_tweet.py)
- Full archive search requires Academic Research or Enterprise tier

**Rate limits:**
- Recent search: 180 requests per 15-minute window (app-level)
- Tweet lookup: 900 requests per 15-minute window
- Stay well under limits with default settings

---

## Skill Configuration

**Edit SKILL.md to customize:**
- When skill should activate (trigger phrases)
- Default search parameters
- Output format preferences

**The skill provides:**
- Content quality evaluation (signal vs noise)
- Source attribution
- Engagement metrics
- Synthesis and analysis

---

## Security

**Never commit credentials:**
- `~/.openclaw/x-api-credentials.json` should be gitignored
- Don't hardcode API keys in scripts
- Use credential file for all API calls

**Credential template provided in `.env.example`**

---

Ready to use after credentials are configured!
