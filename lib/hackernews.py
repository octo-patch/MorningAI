"""Hacker News collector for ai-tracker (Algolia API, free).

Adapted from last30days hackernews.py.
"""

import html
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_HACKERNEWS

ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
ALGOLIA_ITEM_URL = "https://hn.algolia.com/api/v1/items"

DEPTH_CONFIG = {"quick": 15, "default": 30, "deep": 60}
ENRICH_LIMITS = {"quick": 3, "default": 5, "deep": 10}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[HN] {msg}\n")
        sys.stderr.flush()


def _date_to_unix(date_str: str) -> int:
    import datetime
    parts = date_str.split("-")
    dt = datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]), tzinfo=datetime.timezone.utc)
    return int(dt.timestamp())


def _unix_to_date(ts: int) -> str:
    import datetime
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return dt.strftime("%Y-%m-%d")


def _strip_html(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def search(
    query: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search HN via Algolia API."""
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    from_ts = _date_to_unix(from_date)
    to_ts = _date_to_unix(to_date) + 86400

    params = {
        "query": query,
        "tags": "story",
        "numericFilters": f"created_at_i>{from_ts},created_at_i<{to_ts},points>2",
        "hitsPerPage": str(count),
    }
    url = f"{ALGOLIA_SEARCH_URL}?{urlencode(params)}"

    try:
        response = http.get(url, timeout=30)
    except Exception as e:
        _log(f"Search failed: {e}")
        return []

    return response.get("hits", [])


def _fetch_comments(object_id: str, max_comments: int = 5) -> List[str]:
    """Fetch top comments for a story."""
    url = f"{ALGOLIA_ITEM_URL}/{object_id}"
    try:
        data = http.get(url, timeout=15)
    except Exception:
        return []

    children = data.get("children", [])
    real_comments = [c for c in children if c.get("text") and c.get("author")]
    real_comments.sort(key=lambda c: c.get("points") or 0, reverse=True)

    insights = []
    for c in real_comments[:max_comments]:
        text = _strip_html(c.get("text", ""))
        first_sentence = text.split(". ")[0].split("\n")[0][:200]
        if first_sentence:
            insights.append(first_sentence)
    return insights


def collect(
    entities: Dict[str, List[str]],
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> CollectionResult:
    """Collect HN stories for tracked entities.

    Args:
        entities: Dict mapping entity name -> list of search keywords
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_HACKERNEWS)
    all_items = []
    enrich_limit = ENRICH_LIMITS.get(depth, ENRICH_LIMITS["default"])

    for entity_name, keywords in entities.items():
        result.entities_checked += 1
        entity_found = False

        for keyword in keywords:
            hits = search(keyword, from_date, to_date, depth)
            if not hits:
                continue

            for i, hit in enumerate(hits):
                object_id = hit.get("objectID", "")
                points = hit.get("points") or 0
                num_comments_val = hit.get("num_comments") or 0
                created_at_i = hit.get("created_at_i")
                date_str = _unix_to_date(created_at_i) if created_at_i else None
                article_url = hit.get("url") or ""
                hn_url = f"https://news.ycombinator.com/item?id={object_id}"

                rank_score = max(0.3, 1.0 - (i * 0.02))
                engagement_boost = min(0.2, math.log1p(points) / 40)
                relevance = min(1.0, rank_score * 0.7 + engagement_boost + 0.1)

                all_items.append(TrackerItem(
                    id=f"HN-{object_id}",
                    title=hit.get("title", ""),
                    summary=f"HN discussion ({points} pts, {num_comments_val} comments)",
                    entity=entity_name,
                    source=SOURCE_HACKERNEWS,
                    source_url=article_url or hn_url,
                    source_label=f"Hacker News",
                    date=date_str,
                    date_confidence="high" if date_str else "low",
                    raw_text=hit.get("title", ""),
                    engagement=Engagement(points=points, num_comments=num_comments_val),
                    relevance=round(relevance, 2),
                ))
                entity_found = True

        if entity_found:
            result.entities_with_updates += 1

    # Enrich top stories with comments
    top_items = sorted(all_items, key=lambda x: x.engagement.points, reverse=True)[:enrich_limit]
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for item in top_items:
            oid = item.id.replace("HN-", "")
            futures[executor.submit(_fetch_comments, oid)] = item
        for future in as_completed(futures):
            item = futures[future]
            try:
                insights = future.result(timeout=15)
                if insights:
                    item.summary += " | Top insights: " + "; ".join(insights[:3])
            except Exception:
                pass

    result.items = all_items
    _log(f"Collected {len(all_items)} HN stories from {result.entities_checked} entities")
    return result
