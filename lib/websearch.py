"""Web search collector for morning-ai (Brave + Exa backends).

Adapted from last30days brave_search.py and exa_search.py.
Used to monitor official blogs, changelogs, and news sites.
"""

import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_WEB

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"
EXA_URL = "https://api.exa.ai/search"

DEPTH_CONFIG = {"quick": 8, "default": 15, "deep": 25}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[Web] {msg}\n")
        sys.stderr.flush()


def _parse_brave_date(age: str, page_age: str = "") -> Optional[str]:
    """Parse Brave's relative date format to YYYY-MM-DD."""
    text = age or page_age
    if not text:
        return None
    match = re.search(r"(\d+)\s+(hour|day|week|month)", text.lower())
    if not match:
        # Try ISO format
        if re.match(r"\d{4}-\d{2}-\d{2}", text):
            return text[:10]
        return None
    num = int(match.group(1))
    unit = match.group(2)
    now = datetime.now(timezone.utc)
    if unit == "hour":
        dt = now - timedelta(hours=num)
    elif unit == "day":
        dt = now - timedelta(days=num)
    elif unit == "week":
        dt = now - timedelta(weeks=num)
    elif unit == "month":
        dt = now - timedelta(days=num * 30)
    else:
        return None
    return dt.strftime("%Y-%m-%d")


def _brave_freshness(days: int) -> str:
    if days <= 1:
        return "pd"
    elif days <= 7:
        return "pw"
    elif days <= 31:
        return "pm"
    else:
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        end = now.strftime("%Y-%m-%d")
        return f"{start}to{end}"


def search_brave(
    query: str,
    entity: str,
    from_date: str,
    to_date: str,
    api_key: str,
    depth: str = "default",
) -> List[TrackerItem]:
    """Search via Brave Web Search API."""
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    now = datetime.now(timezone.utc)
    start = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    days = (now - start).days

    params = {
        "q": query,
        "result_filter": "web,news",
        "count": str(count),
        "safesearch": "off",
        "freshness": _brave_freshness(max(1, days)),
    }
    url = f"{BRAVE_URL}?{urlencode(params)}"
    headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}

    try:
        response = http.get(url, headers=headers, timeout=30)
    except Exception as e:
        _log(f"Brave search '{query}' failed: {e}")
        return []

    items = []
    web_results = response.get("web", {}).get("results", [])
    news_results = response.get("news", {}).get("results", [])
    all_results = web_results + news_results

    for i, r in enumerate(all_results[:count]):
        date = _parse_brave_date(r.get("age", ""), r.get("page_age", ""))
        if not date and r.get("meta_url", {}).get("date"):
            raw_date = r["meta_url"]["date"]
            if re.match(r"\d{4}-\d{2}-\d{2}", str(raw_date)):
                date = str(raw_date)[:10]

        items.append(TrackerItem(
            id=f"WEB-brave-{i}",
            title=r.get("title", ""),
            summary=r.get("description", "")[:300],
            entity=entity,
            source=SOURCE_WEB,
            source_url=r.get("url", ""),
            source_label=r.get("meta_url", {}).get("hostname", "web"),
            date=date,
            date_confidence="med" if date else "low",
            raw_text=r.get("description", ""),
            relevance=0.6,
        ))

    _log(f"Brave '{query}': {len(items)} results")
    return items


def search_exa(
    query: str,
    entity: str,
    from_date: str,
    to_date: str,
    api_key: str,
    depth: str = "default",
) -> List[TrackerItem]:
    """Search via Exa AI API."""
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])

    payload = {
        "query": query,
        "type": "auto",
        "numResults": count,
        "contents": {"text": {"maxCharacters": 2000}},
        "startPublishedDate": f"{from_date}T00:00:00.000Z",
        "endPublishedDate": f"{to_date}T23:59:59.999Z",
    }
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    try:
        response = http.post(EXA_URL, json_data=payload, headers=headers, timeout=30)
    except Exception as e:
        _log(f"Exa search '{query}' failed: {e}")
        return []

    items = []
    results = response.get("results", [])

    for i, r in enumerate(results[:count]):
        date = None
        pub_date = r.get("publishedDate", "")
        if pub_date and len(pub_date) >= 10:
            date = pub_date[:10]

        exa_score = r.get("score", 0.6)
        relevance = max(0.0, min(1.0, exa_score))

        items.append(TrackerItem(
            id=f"WEB-exa-{i}",
            title=r.get("title", ""),
            summary=(r.get("text", "") or "")[:300],
            entity=entity,
            source=SOURCE_WEB,
            source_url=r.get("url", ""),
            source_label=r.get("url", "").split("/")[2] if "/" in r.get("url", "") else "web",
            date=date,
            date_confidence="med" if date else "low",
            raw_text=(r.get("text", "") or "")[:1000],
            relevance=round(relevance, 2),
        ))

    _log(f"Exa '{query}': {len(items)} results")
    return items


def collect(
    entities: Dict[str, List[str]],
    from_date: str,
    to_date: str,
    brave_key: Optional[str] = None,
    exa_key: Optional[str] = None,
    depth: str = "default",
) -> CollectionResult:
    """Collect web search results for tracked entities.

    Args:
        entities: Dict mapping entity name -> list of search queries
            (e.g. site-specific: "site:openai.com/blog")
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        brave_key: Brave API key (optional)
        exa_key: Exa API key (optional)
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_WEB)
    all_items = []

    if not brave_key and not exa_key:
        result.errors.append("No web search API key configured (BRAVE_API_KEY or EXA_API_KEY)")
        return result

    for entity_name, queries in entities.items():
        result.entities_checked += 1
        entity_found = False

        for query in queries:
            if brave_key:
                items = search_brave(query, entity_name, from_date, to_date, brave_key, depth)
                if items:
                    all_items.extend(items)
                    entity_found = True
            elif exa_key:
                items = search_exa(query, entity_name, from_date, to_date, exa_key, depth)
                if items:
                    all_items.extend(items)
                    entity_found = True

        if entity_found:
            result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} web results from {result.entities_checked} entities")
    return result
