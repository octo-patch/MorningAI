"""Reddit collector for morning-ai (public JSON, no API key needed).

Adapted from last30days reddit_public.py.
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_REDDIT

USER_AGENT = "morning-ai/1.0 (AI Industry Tracker)"

DEPTH_LIMITS = {
    "quick": 10,
    "default": 25,
    "deep": 50,
}

# AI-focused subreddits
DEFAULT_SUBREDDITS = ["MachineLearning", "LocalLLaMA", "artificial", "singularity"]

MAX_RETRIES = 3
BASE_BACKOFF = 2.0


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[Reddit] {msg}\n")
        sys.stderr.flush()


def _fetch_json(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if "json" not in content_type and "text/html" in content_type:
                    return None
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                delay = BASE_BACKOFF * (2 ** attempt)
                _log(f"429 rate limited, retry after {delay:.1f}s")
                time.sleep(delay)
                continue
            return None
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            return None
    return None


def _parse_date(created_utc: Any) -> Optional[str]:
    if not created_utc:
        return None
    try:
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(float(created_utc), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return None


def search_subreddit(
    query: str,
    subreddit: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[TrackerItem]:
    """Search a subreddit via public JSON endpoint."""
    limit = DEPTH_LIMITS.get(depth, DEPTH_LIMITS["default"])
    encoded = urllib.parse.quote_plus(query)
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={encoded}&restrict_sr=on&sort=relevance&t=month&limit={limit}&raw_json=1"
    )

    data = _fetch_json(url)
    if not data:
        return []

    children = data.get("data", {}).get("children", [])
    items = []

    for i, child in enumerate(children):
        if child.get("kind") != "t3":
            continue
        post = child.get("data", {})
        permalink = str(post.get("permalink", "")).strip()
        if not permalink or "/comments/" not in permalink:
            continue

        date = _parse_date(post.get("created_utc"))
        if date and (date < from_date or date > to_date):
            continue

        score_val = int(post.get("score", 0) or 0)
        num_comments = int(post.get("num_comments", 0) or 0)

        items.append(TrackerItem(
            id=f"R-{subreddit}-{i}",
            title=str(post.get("title", "")).strip(),
            summary=str(post.get("selftext", ""))[:300],
            entity=query,
            source=SOURCE_REDDIT,
            source_url=f"https://www.reddit.com{permalink}",
            source_label=f"r/{subreddit}",
            date=date,
            date_confidence="high" if date else "low",
            raw_text=str(post.get("selftext", "")),
            engagement=Engagement(
                score=score_val,
                num_comments=num_comments,
                upvote_ratio=float(post.get("upvote_ratio", 0) or 0),
            ),
            relevance=_compute_relevance(score_val, num_comments),
        ))

    _log(f"r/{subreddit} '{query}': {len(items)} posts")
    return items


def _compute_relevance(score: int, num_comments: int) -> float:
    score_c = min(1.0, max(0.0, score / 500.0))
    comments_c = min(1.0, max(0.0, num_comments / 200.0))
    return round(score_c * 0.6 + comments_c * 0.4, 3)


def fetch_subreddit(
    subreddit: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[TrackerItem]:
    """Fetch hot posts from a dedicated subreddit (no keyword filter).

    Used for entity-specific subreddits where all posts are relevant.
    """
    limit = DEPTH_LIMITS.get(depth, DEPTH_LIMITS["default"])
    url = (
        f"https://www.reddit.com/r/{subreddit}/hot.json"
        f"?limit={limit}&raw_json=1"
    )

    data = _fetch_json(url)
    if not data:
        return []

    children = data.get("data", {}).get("children", [])
    items = []

    for i, child in enumerate(children):
        if child.get("kind") != "t3":
            continue
        post = child.get("data", {})
        permalink = str(post.get("permalink", "")).strip()
        if not permalink or "/comments/" not in permalink:
            continue

        # Skip pinned/stickied posts
        if post.get("stickied"):
            continue

        date = _parse_date(post.get("created_utc"))
        if date and (date < from_date or date > to_date):
            continue

        score_val = int(post.get("score", 0) or 0)
        num_comments = int(post.get("num_comments", 0) or 0)

        items.append(TrackerItem(
            id=f"R-{subreddit}-h{i}",
            title=str(post.get("title", "")).strip(),
            summary=str(post.get("selftext", ""))[:300],
            entity="",  # filled by caller
            source=SOURCE_REDDIT,
            source_url=f"https://www.reddit.com{permalink}",
            source_label=f"r/{subreddit}",
            date=date,
            date_confidence="high" if date else "low",
            raw_text=str(post.get("selftext", "")),
            engagement=Engagement(
                score=score_val,
                num_comments=num_comments,
                upvote_ratio=float(post.get("upvote_ratio", 0) or 0),
            ),
            relevance=_compute_relevance(score_val, num_comments),
        ))

    _log(f"r/{subreddit} (hot): {len(items)} posts")
    return items


def collect(
    entities: Dict[str, List[str]],
    from_date: str,
    to_date: str,
    entity_subreddits: Optional[Dict[str, List[str]]] = None,
    subreddits: Optional[List[str]] = None,
    depth: str = "default",
) -> CollectionResult:
    """Collect Reddit posts for tracked entities.

    Args:
        entities: Dict mapping entity name -> list of search keywords
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        entity_subreddits: Dict mapping entity name -> list of dedicated subreddit names
        subreddits: General subreddits to search (default: AI-focused)
        depth: Search depth

    Returns:
        CollectionResult
    """
    subs = subreddits or DEFAULT_SUBREDDITS
    result = CollectionResult(source=SOURCE_REDDIT)
    all_items = []
    seen_urls = set()

    # Phase 1: Fetch hot posts from entity-specific subreddits (concurrent)
    if entity_subreddits:
        phase1_tasks = []
        for entity_name, entity_subs in entity_subreddits.items():
            result.entities_checked += 1
            for sub in entity_subs:
                phase1_tasks.append((entity_name, sub))

        phase1_results: Dict[str, List[TrackerItem]] = {}
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {
                pool.submit(fetch_subreddit, sub, from_date, to_date, depth): (entity_name, sub)
                for entity_name, sub in phase1_tasks
            }
            for future in as_completed(futures):
                entity_name, sub = futures[future]
                try:
                    items = future.result()
                except Exception:
                    items = []
                if items:
                    for item in items:
                        item.entity = entity_name
                        seen_urls.add(item.source_url)
                    phase1_results.setdefault(entity_name, []).extend(items)

        for entity_name, items in phase1_results.items():
            all_items.extend(items)
            result.entities_with_updates += 1

    # Phase 2: Keyword search in general subreddits (concurrent)
    phase2_tasks = []
    for entity_name, keywords in entities.items():
        if entity_name not in (entity_subreddits or {}):
            result.entities_checked += 1
        for keyword in keywords:
            for sub in subs:
                phase2_tasks.append((entity_name, keyword, sub))

    phase2_results: Dict[str, List[TrackerItem]] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(search_subreddit, keyword, sub, from_date, to_date, depth): (entity_name, keyword, sub)
            for entity_name, keyword, sub in phase2_tasks
        }
        for future in as_completed(futures):
            entity_name, keyword, sub = futures[future]
            try:
                items = future.result()
            except Exception:
                items = []
            if items:
                for item in items:
                    item.entity = entity_name
                # Dedupe against entity-specific results
                items = [i for i in items if i.source_url not in seen_urls]
                for item in items:
                    seen_urls.add(item.source_url)
                phase2_results.setdefault(entity_name, []).extend(items)

    for entity_name, items in phase2_results.items():
        all_items.extend(items)
        if entity_name not in (entity_subreddits or {}):
            result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} Reddit posts from {result.entities_checked} entities")
    return result
