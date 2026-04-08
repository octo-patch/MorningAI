"""X/Twitter collector for ai-tracker.

Searches X via public JSON endpoints or ScrapeCreators API.
Adapted from last30days bird_x.py and scrapecreators_x.py.
"""

import sys
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, quote_plus

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_X

SCRAPECREATORS_BASE = "https://api.scrapecreators.com/v1/twitter"

DEPTH_CONFIG = {
    "quick": 10,
    "default": 20,
    "deep": 40,
}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[X] {msg}\n")
        sys.stderr.flush()


def _parse_date(raw: Any) -> Optional[str]:
    """Parse various X date formats to YYYY-MM-DD."""
    if not raw:
        return None
    if isinstance(raw, (int, float)):
        import datetime
        dt = datetime.datetime.fromtimestamp(raw, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d")
    s = str(raw)
    # ISO format: 2026-04-03T12:00:00Z
    if "T" in s and len(s) >= 10:
        return s[:10]
    # Twitter format: Wed Jan 15 14:30:00 +0000 2026
    if len(s) > 20 and s[3] == " ":
        try:
            import datetime
            dt = datetime.datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def _parse_engagement(raw: Dict[str, Any]) -> Engagement:
    """Extract engagement from raw tweet data."""
    return Engagement(
        likes=int(raw.get("favorite_count") or raw.get("likes") or raw.get("likeCount") or raw.get("like_count") or 0),
        reposts=int(raw.get("retweet_count") or raw.get("reposts") or raw.get("retweetCount") or raw.get("repost_count") or 0),
        replies=int(raw.get("reply_count") or raw.get("replies") or raw.get("replyCount") or 0),
        quotes=int(raw.get("quote_count") or raw.get("quotes") or raw.get("quoteCount") or 0),
    )


def search_handles(
    handles: List[str],
    entity: str,
    from_date: str,
    to_date: str,
    api_key: str,
    depth: str = "default",
) -> List[TrackerItem]:
    """Search tweets from specific handles via ScrapeCreators.

    Args:
        handles: List of X handles (without @)
        entity: Entity name (e.g. "OpenAI")
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        api_key: ScrapeCreators API key
        depth: Search depth

    Returns:
        List of TrackerItem
    """
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    items = []

    for handle in handles:
        handle = handle.lstrip("@")
        query = f"from:{handle} since:{from_date} until:{to_date}"

        try:
            params = urlencode({"query": query, "sort_by": "relevance"})
            url = f"{SCRAPECREATORS_BASE}/search/tweets?{params}"
            headers = {"x-api-key": api_key}
            response = http.get(url, headers=headers, timeout=30)
        except http.HTTPError as e:
            _log(f"Failed to search @{handle}: {e}")
            continue
        except Exception as e:
            _log(f"Failed to search @{handle}: {e}")
            continue

        tweets = response.get("tweets") or response.get("data") or response.get("results") or []
        if isinstance(tweets, dict):
            tweets = tweets.get("results", [])

        _log(f"@{handle}: found {len(tweets)} tweets")

        for i, tweet in enumerate(tweets[:count]):
            text = tweet.get("text") or tweet.get("full_text") or ""
            date = _parse_date(tweet.get("created_at") or tweet.get("date"))

            # Date filter
            if date and (date < from_date or date > to_date):
                continue

            engagement = _parse_engagement(tweet)
            total_eng = engagement.likes + engagement.reposts + engagement.replies

            items.append(TrackerItem(
                id=f"X-{handle}-{i}",
                title=text[:120] + ("..." if len(text) > 120 else ""),
                summary=text[:300],
                entity=entity,
                source=SOURCE_X,
                source_url=tweet.get("url") or f"https://x.com/{handle}/status/{tweet.get('id', '')}",
                source_label=f"@{handle} on X",
                date=date,
                date_confidence="high" if date else "low",
                raw_text=text,
                engagement=engagement,
                relevance=min(1.0, 0.5 + min(0.5, total_eng / 1000)),
            ))

    return items


def search_topic(
    topic: str,
    entity: str,
    from_date: str,
    to_date: str,
    api_key: str,
    depth: str = "default",
) -> List[TrackerItem]:
    """Search X for a topic keyword via ScrapeCreators.

    Args:
        topic: Search keyword
        entity: Entity name
        from_date: Start date
        to_date: End date
        api_key: ScrapeCreators API key
        depth: Search depth

    Returns:
        List of TrackerItem
    """
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    query = f"{topic} since:{from_date} until:{to_date}"

    try:
        params = urlencode({"query": query, "sort_by": "relevance"})
        url = f"{SCRAPECREATORS_BASE}/search/tweets?{params}"
        headers = {"x-api-key": api_key}
        response = http.get(url, headers=headers, timeout=30)
    except (http.HTTPError, Exception) as e:
        _log(f"Topic search '{topic}' failed: {e}")
        return []

    tweets = response.get("tweets") or response.get("data") or response.get("results") or []
    if isinstance(tweets, dict):
        tweets = tweets.get("results", [])

    items = []
    for i, tweet in enumerate(tweets[:count]):
        text = tweet.get("text") or tweet.get("full_text") or ""
        date = _parse_date(tweet.get("created_at") or tweet.get("date"))
        handle = tweet.get("user", {}).get("screen_name") or tweet.get("author_handle") or ""

        if date and (date < from_date or date > to_date):
            continue

        engagement = _parse_engagement(tweet)
        total_eng = engagement.likes + engagement.reposts

        items.append(TrackerItem(
            id=f"X-{topic[:20]}-{i}",
            title=text[:120] + ("..." if len(text) > 120 else ""),
            summary=text[:300],
            entity=entity,
            source=SOURCE_X,
            source_url=tweet.get("url") or f"https://x.com/{handle}/status/{tweet.get('id', '')}",
            source_label=f"@{handle} on X" if handle else "X search",
            date=date,
            date_confidence="high" if date else "low",
            raw_text=text,
            engagement=engagement,
            relevance=min(1.0, 0.4 + min(0.6, total_eng / 500)),
        ))

    return items


def collect(
    entities: Dict[str, List[str]],
    from_date: str,
    to_date: str,
    api_key: str,
    depth: str = "default",
) -> CollectionResult:
    """Collect X/Twitter data for all tracked entities.

    Args:
        entities: Dict mapping entity name -> list of X handles
        from_date: Start date
        to_date: End date
        api_key: ScrapeCreators API key
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_X)
    all_items = []

    for entity_name, handles in entities.items():
        result.entities_checked += 1
        try:
            items = search_handles(handles, entity_name, from_date, to_date, api_key, depth)
            if items:
                result.entities_with_updates += 1
                all_items.extend(items)
        except Exception as e:
            result.errors.append(f"{entity_name}: {e}")

    result.items = all_items
    _log(f"Collected {len(all_items)} tweets from {result.entities_checked} entities")
    return result
