#!/usr/bin/env python3
"""
fetch-tweet.py — Fetch and archive a tweet from X/Twitter
Usage: python3 fetch-tweet.py <tweet_url> [--tag trading|self-improvement|tool|crypto|other] [--note "optional note"]

Tries X API Bearer Token first (if ~/.openclaw/workspace/.secrets/x_bearer_token exists),
falls back to web_fetch via HTTP.

Output: appends to links/YYYY-MM-DD.md
"""

import sys
import os
import re
import json
import html as html_module
import hmac
import hashlib
import base64
import time
import uuid
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS_DIR = os.path.join(WORKSPACE, "links")
SECRETS_DIR = os.path.join(WORKSPACE, ".secrets")
BEARER_TOKEN_PATH = os.path.join(SECRETS_DIR, "x_bearer_token")

def extract_tweet_id(url: str) -> str | None:
    """Extract tweet ID from various X/Twitter URL formats."""
    patterns = [
        r"(?:twitter\.com|x\.com)/\w+/status/(\d+)",
        r"(?:twitter\.com|x\.com)/i/web/status/(\d+)",
        r"/status/(\d+)",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def load_bearer_token() -> str | None:
    if os.path.exists(BEARER_TOKEN_PATH):
        with open(BEARER_TOKEN_PATH) as f:
            return f.read().strip()
    return os.environ.get("X_BEARER_TOKEN")

def load_oauth_creds() -> dict | None:
    """Load OAuth 1.0a credentials for write actions (follow, etc.)."""
    paths = {
        "api_key": os.path.join(SECRETS_DIR, "x_api_key"),
        "api_secret": os.path.join(SECRETS_DIR, "x_api_secret"),
        "access_token": os.path.join(SECRETS_DIR, "x_access_token"),
        "access_secret": os.path.join(SECRETS_DIR, "x_access_secret"),
    }
    creds = {}
    for k, p in paths.items():
        if not os.path.exists(p):
            return None
        with open(p) as f:
            creds[k] = f.read().strip()
    return creds

def oauth1_header(method: str, url: str, creds: dict, extra_params: dict = {}) -> str:
    """Generate OAuth 1.0a Authorization header."""
    params = {
        "oauth_consumer_key": creds["api_key"],
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": creds["access_token"],
        "oauth_version": "1.0",
    }
    all_params = {**params, **extra_params}
    sorted_params = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in sorted(all_params.items())
    )
    base = "&".join([
        method.upper(),
        urllib.parse.quote(url, safe=""),
        urllib.parse.quote(sorted_params, safe=""),
    ])
    signing_key = f"{urllib.parse.quote(creds['api_secret'], safe='')}&{urllib.parse.quote(creds['access_secret'], safe='')}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    params["oauth_signature"] = sig
    header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(str(v), safe="")}"'
        for k, v in sorted(params.items())
    )
    return header

def get_user_id(handle: str, bearer_token: str) -> str | None:
    """Look up a user's numeric ID by their handle."""
    url = f"https://api.twitter.com/2/users/by/username/{handle}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer_token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("data", {}).get("id")
    except Exception as e:
        print(f"[follow] Could not look up user @{handle}: {e}", file=sys.stderr)
        return None

def follow_user(handle: str, user_id: str) -> bool:
    """Follow a user via OAuth 1.0a. Returns True on success."""
    creds = load_oauth_creds()
    bearer = load_bearer_token()
    if not creds or not bearer:
        print("[follow] Missing OAuth credentials", file=sys.stderr)
        return False

    target_id = get_user_id(handle, bearer)
    if not target_id:
        return False

    # Authenticated user ID is embedded in access token
    auth_user_id = creds["access_token"].split("-")[0]
    url = f"https://api.twitter.com/2/users/{auth_user_id}/following"
    body = json.dumps({"target_user_id": target_id}).encode()

    auth_header = oauth1_header("POST", url, creds)
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            following = result.get("data", {}).get("following", False)
            pending = result.get("data", {}).get("pending_follow", False)
            if following:
                print(f"[follow] ✅ Now following @{handle}")
            elif pending:
                print(f"[follow] ⏳ Follow request sent to @{handle} (private account)")
            return following or pending
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()
        print(f"[follow] HTTP {e.code}: {body_err}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[follow] Error: {e}", file=sys.stderr)
        return False

def load_oauth2_token() -> str | None:
    """Load OAuth 2.0 user access token for bookmark actions."""
    token_path = os.path.join(SECRETS_DIR, "x_oauth2_token.json")
    if not os.path.exists(token_path):
        return None
    with open(token_path) as f:
        data = json.load(f)
    return data.get("access_token")

def bookmark_tweet(tweet_id: str) -> bool:
    """Bookmark a tweet via OAuth 2.0."""
    token = load_oauth2_token()
    if not token:
        print("[bookmark] No OAuth 2.0 token — run scripts/x-oauth2-setup.py first", file=sys.stderr)
        return False

    bearer = load_bearer_token()
    # Need authenticated user ID
    url_me = "https://api.twitter.com/2/users/me"
    try:
        req = urllib.request.Request(url_me, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            me = json.loads(resp.read())
            user_id = me["data"]["id"]
    except Exception as e:
        print(f"[bookmark] Could not get user ID: {e}", file=sys.stderr)
        return False

    url = f"https://api.twitter.com/2/users/{user_id}/bookmarks"
    body = json.dumps({"tweet_id": tweet_id}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("data", {}).get("bookmarked"):
                print(f"[bookmark] 🔖 Bookmarked tweet {tweet_id}")
                return True
    except urllib.error.HTTPError as e:
        print(f"[bookmark] HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
    except Exception as e:
        print(f"[bookmark] Error: {e}", file=sys.stderr)
    return False

def fetch_thread_via_api(conversation_id: str, author_id: str, token: str) -> list[dict]:
    """Fetch all tweets in a thread/conversation by the same author."""
    query = urllib.parse.quote(f"conversation_id:{conversation_id} from:{author_id} -is:retweet")
    url = (
        f"https://api.twitter.com/2/tweets/search/recent"
        f"?query={query}"
        f"&max_results=100"
        f"&tweet.fields=created_at,author_id,text,id"
        f"&expansions=author_id"
        f"&user.fields=name,username"
        f"&sort_order=recency"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            tweets = data.get("data", [])
            # Sort oldest first (thread order)
            tweets.sort(key=lambda t: t.get("id", "0"))
            return [t.get("text", "") for t in tweets]
    except Exception as e:
        print(f"[thread] Failed to fetch thread: {e}", file=sys.stderr)
        return []

def fetch_via_api(tweet_id: str, token: str) -> dict | None:
    """Fetch tweet via X API v2. Detects threads and fetches all parts."""
    url = (
        f"https://api.twitter.com/2/tweets/{tweet_id}"
        f"?tweet.fields=created_at,author_id,text,entities,public_metrics,conversation_id"
        f"&expansions=author_id"
        f"&user.fields=name,username"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            tweet = data.get("data", {})
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            author = users.get(tweet.get("author_id", ""), {})
            conversation_id = tweet.get("conversation_id", tweet_id)

            # Detect thread: conversation_id differs from tweet_id (reply in a thread)
            # or try fetching conversation to see if there are more tweets
            thread_tweets = []
            if conversation_id:
                thread_tweets = fetch_thread_via_api(
                    conversation_id, tweet.get("author_id", ""), token
                )
                # Filter out duplicates and ensure root tweet is included
                root_text = tweet.get("text", "")
                if root_text not in thread_tweets:
                    thread_tweets = [root_text] + thread_tweets

            return {
                "id": tweet_id,
                "text": tweet.get("text", ""),
                "thread": thread_tweets if len(thread_tweets) > 1 else [],
                "author_name": author.get("name", "Unknown"),
                "author_handle": author.get("username", "unknown"),
                "created_at": tweet.get("created_at", ""),
                "source": "x_api",
            }
    except Exception as e:
        print(f"[API] Failed: {e}", file=sys.stderr)
        return None

def fetch_via_oembed(url: str) -> dict | None:
    """Try Twitter's public oEmbed endpoint — no auth required."""
    tweet_id = extract_tweet_id(url)
    oembed_url = f"https://publish.twitter.com/oembed?url={urllib.parse.quote(url)}&omit_script=true"
    try:
        req = urllib.request.Request(
            oembed_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SCV-bot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            html_content = data.get("html", "")
            author_name = data.get("author_name", "")
            author_url = data.get("author_url", "")
            # Extract handle from author_url (https://twitter.com/handle)
            handle_m = re.search(r"twitter\.com/(\w+)$", author_url)
            handle = handle_m.group(1) if handle_m else ""
            # Strip HTML tags from embedded html to get plain text
            text = re.sub(r'<[^>]+>', '', html_content).strip()
            # Decode HTML entities and clean whitespace
            text = html_module.unescape(text)
            text = re.sub(r'\n{3,}', '\n\n', text).strip()
            if text:
                return {
                    "id": tweet_id or "unknown",
                    "text": text,
                    "author_name": author_name,
                    "author_handle": handle,
                    "created_at": "",
                    "source": "oembed",
                }
    except Exception as e:
        print(f"[oEmbed] Failed: {e}", file=sys.stderr)
    return None

def fetch_via_web(url: str) -> dict | None:
    """Fallback: try nitter mirrors."""
    tweet_id = extract_tweet_id(url)
    nitter_instances = [
        f"https://nitter.poast.org/i/status/{tweet_id}",
        f"https://nitter.cz/i/status/{tweet_id}",
        f"https://nitter.net/i/status/{tweet_id}",
    ]

    for fetch_url in nitter_instances:
        try:
            req = urllib.request.Request(
                fetch_url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SCV-bot/1.0)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                m = re.search(r'<meta\s+(?:name|property)=["\'](?:og:description|twitter:description)["\'][^>]+content=["\'](.*?)["\']', html, re.DOTALL | re.IGNORECASE)
                if not m:
                    m = re.search(r'content=["\'](.*?)["\']\s+(?:name|property)=["\'](?:og:description|twitter:description)["\']', html, re.DOTALL | re.IGNORECASE)
                if m:
                    text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    title_m = re.search(r'<meta\s+(?:name|property)=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
                    author_name = ""
                    if title_m:
                        title = title_m.group(1)
                        a = re.match(r'^(.+?)\s+on\s+(?:Twitter|X|Nitter)', title)
                        if a:
                            author_name = a.group(1)
                    return {
                        "id": tweet_id or "unknown",
                        "text": text,
                        "author_name": author_name,
                        "author_handle": "",
                        "created_at": "",
                        "source": "web_scrape",
                    }
        except Exception as e:
            print(f"[Web] Failed {fetch_url}: {e}", file=sys.stderr)
    return None

def archive_tweet(url: str, tweet: dict, tag: str = "other", note: str = "") -> str:
    """Append tweet to today's archive file."""
    today = datetime.now().strftime("%Y-%m-%d")
    archive_path = os.path.join(LINKS_DIR, f"{today}.md")

    now = datetime.now().strftime("%H:%M")
    handle = f"@{tweet['author_handle']}" if tweet['author_handle'] else tweet['author_name']
    source_map = {"x_api": "✅ API", "oembed": "✅ oEmbed", "web_scrape": "⚠️ scraped"}
    source_badge = source_map.get(tweet['source'], "⚠️ unknown")

    thread = tweet.get("thread", [])
    is_thread = len(thread) > 1

    entry = f"""
---
### [{now}] {handle} `#{tag}` {source_badge}{' 🧵 thread' if is_thread else ''}
**URL:** {url}
"""
    if is_thread:
        entry += "**Thread:**\n"
        for i, t in enumerate(thread, 1):
            entry += f"{i}. {t}\n\n"
    else:
        entry += f"**Tweet:** {tweet['text']}\n"

    if note:
        entry += f"**Note:** {note}\n"
    if tweet['created_at']:
        entry += f"**Posted:** {tweet['created_at']}\n"

    # Create file with header if new
    if not os.path.exists(archive_path):
        with open(archive_path, "w") as f:
            f.write(f"# Tweet Archive — {today}\n")

    with open(archive_path, "a") as f:
        f.write(entry)

    return archive_path

def main():
    if len(sys.argv) < 2:
        print("Usage: fetch-tweet.py <url> [--tag TAG] [--note NOTE]")
        sys.exit(1)

    url = sys.argv[1]
    tag = "other"
    note = ""
    do_follow = False
    do_bookmark = False

    # Parse optional args
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == "--tag" and i + 1 < len(args):
            tag = args[i + 1]
        elif a == "--note" and i + 1 < len(args):
            note = args[i + 1]
        elif a == "--follow":
            do_follow = True
        elif a == "--bookmark":
            do_bookmark = True

    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        print(f"ERROR: Could not extract tweet ID from URL: {url}")
        sys.exit(1)

    print(f"Tweet ID: {tweet_id}")

    # Try API first
    token = load_bearer_token()
    tweet = None
    if token:
        print("Trying X API...")
        tweet = fetch_via_api(tweet_id, token)

    # Fallback to oEmbed
    if not tweet:
        print("Trying oEmbed...")
        tweet = fetch_via_oembed(url)

    # Fallback to web scrape
    if not tweet:
        print("Trying web scrape...")
        tweet = fetch_via_web(url)

    if not tweet:
        print("ERROR: Could not fetch tweet — refusing to archive without real content.")
        sys.exit(2)

    path = archive_tweet(url, tweet, tag=tag, note=note)
    thread = tweet.get("thread", [])
    print(f"Archived → {path}")
    print(f"Author: {tweet['author_name']} ({tweet['author_handle']})")
    if len(thread) > 1:
        print(f"Thread: {len(thread)} tweets")
        for i, t in enumerate(thread, 1):
            print(f"  {i}. {t[:100]}{'...' if len(t) > 100 else ''}")
    else:
        print(f"Text: {tweet['text'][:200]}")
    print(f"Source: {tweet['source']}")

    if do_follow and tweet.get("author_handle"):
        follow_user(tweet["author_handle"], tweet.get("id", ""))

    if do_bookmark:
        bookmark_tweet(tweet_id)

if __name__ == "__main__":
    main()
