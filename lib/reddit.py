"""Reddit collector for morning-ai (public Atom RSS feeds, no API key needed).

History: originally hit the public ``*.json`` endpoints, but Reddit started
returning 403 to all unauthenticated JSON requests in late 2024. The
``*.rss`` (Atom) feeds remain open and serve the same posts — at the cost of
losing per-post engagement (score / num_comments / upvote_ratio), which
RSS does not expose. We fall back to a flat relevance and zero engagement;
ranking degrades gracefully because Reddit pre-orders the feed by hotness
or relevance server-side.

Switch back to JSON only if Reddit re-opens the endpoint, or migrate to
OAuth (oauth.reddit.com) and add REDDIT_CLIENT_ID/SECRET env vars.
"""

import html
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_REDDIT
from .util import log

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

# Without per-post score we can't rank — give every RSS-sourced item the same
# mid-band relevance so downstream score.py still has a numeric to work with.
RSS_DEFAULT_RELEVANCE = 0.3

DEPTH_LIMITS = {
    "quick": 10,
    "default": 25,
    "deep": 50,
}

# AI-focused subreddits
DEFAULT_SUBREDDITS = ["MachineLearning", "LocalLLaMA", "artificial", "singularity"]


_log = lambda msg: log("Reddit", msg, tty_only=True)


def _fetch_text(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch a URL and return the response body as text (or None on failure).

    Delegates retry, backoff, and IPv4 fallback to lib.http.
    """
    try:
        return http.get_text(
            url,
            headers={"Accept": "application/atom+xml, application/xml, text/xml"},
            timeout=timeout,
            retries=3,
        )
    except http.HTTPError as e:
        _log(f"fetch failed for {url}: {e}")
        return None


def _extract_summary(content_html: str) -> str:
    """Pull a short plain-text snippet out of an Atom <content type=html> body.

    Reddit wraps the post body in ``<!-- SC_OFF --> ... <!-- SC_ON -->``,
    followed by a "submitted by ..." footer we don't want.
    """
    if not content_html:
        return ""
    decoded = html.unescape(content_html)
    if "<!-- SC_ON -->" in decoded:
        decoded = decoded.split("<!-- SC_ON -->", 1)[0]
    if "<!-- SC_OFF -->" in decoded:
        decoded = decoded.split("<!-- SC_OFF -->", 1)[1]
    text = re.sub(r"<[^>]+>", " ", decoded)
    return " ".join(text.split())[:300]


def _parse_rss(xml_text: str) -> List[Dict[str, str]]:
    """Parse a Reddit Atom feed into a list of normalized post dicts.

    Returns dicts with: id (t3_xxx), title, url, date (YYYY-MM-DD), summary.
    """
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        _log(f"RSS parse error: {e}")
        return []

    out: List[Dict[str, str]] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title = (entry.findtext("atom:title", default="", namespaces=ATOM_NS) or "").strip()
        post_id = (entry.findtext("atom:id", default="", namespaces=ATOM_NS) or "").strip()
        link_el = entry.find("atom:link", ATOM_NS)
        url = link_el.get("href", "").strip() if link_el is not None else ""
        if not url or "/comments/" not in url:
            continue
        published = (entry.findtext("atom:published", default="", namespaces=ATOM_NS) or "")
        date = published[:10] if len(published) >= 10 else None
        content = entry.findtext("atom:content", default="", namespaces=ATOM_NS) or ""
        out.append({
            "id": post_id,
            "title": title,
            "url": url,
            "date": date or "",
            "summary": _extract_summary(content),
        })
    return out


def search_subreddit(
    query: str,
    subreddit: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[TrackerItem]:
    """Search a subreddit via the public Atom RSS endpoint."""
    limit = DEPTH_LIMITS.get(depth, DEPTH_LIMITS["default"])
    encoded = urllib.parse.quote_plus(query)
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.rss"
        f"?q={encoded}&restrict_sr=on&sort=relevance&t=month&limit={limit}"
    )

    body = _fetch_text(url)
    posts = _parse_rss(body) if body else []

    items: List[TrackerItem] = []
    for i, post in enumerate(posts):
        date = post["date"] or None
        if date and (date < from_date or date > to_date):
            continue
        items.append(TrackerItem(
            id=f"R-{subreddit}-{i}",
            title=post["title"],
            summary=post["summary"],
            entity=query,
            source=SOURCE_REDDIT,
            source_url=post["url"],
            source_label=f"r/{subreddit}",
            date=date,
            date_confidence="high" if date else "low",
            raw_text=post["summary"],
            engagement=Engagement(
                score=0,
                num_comments=0,
                upvote_ratio=0.0,
            ),
            relevance=RSS_DEFAULT_RELEVANCE,
        ))

    _log(f"r/{subreddit} '{query}': {len(items)} posts")
    return items


def _compute_relevance(score: int, num_comments: int) -> float:
    """Legacy JSON-era relevance scorer.

    Kept for callers that still pass real engagement numbers; RSS path now
    uses RSS_DEFAULT_RELEVANCE because score/num_comments are unavailable.
    """
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
    url = f"https://www.reddit.com/r/{subreddit}/hot.rss?limit={limit}"

    body = _fetch_text(url)
    posts = _parse_rss(body) if body else []

    items: List[TrackerItem] = []
    for i, post in enumerate(posts):
        date = post["date"] or None
        if date and (date < from_date or date > to_date):
            continue
        items.append(TrackerItem(
            id=f"R-{subreddit}-h{i}",
            title=post["title"],
            summary=post["summary"],
            entity="",  # filled by caller
            source=SOURCE_REDDIT,
            source_url=post["url"],
            source_label=f"r/{subreddit}",
            date=date,
            date_confidence="high" if date else "low",
            raw_text=post["summary"],
            engagement=Engagement(
                score=0,
                num_comments=0,
                upvote_ratio=0.0,
            ),
            relevance=RSS_DEFAULT_RELEVANCE,
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
