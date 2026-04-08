"""HuggingFace collector for ai-tracker.

Monitors model/space/dataset updates via HuggingFace API.
New collector — no last30days equivalent.
"""

import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, quote

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_HUGGINGFACE

HF_API = "https://huggingface.co/api"

DEPTH_CONFIG = {"quick": 5, "default": 10, "deep": 20}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[HF] {msg}\n")
        sys.stderr.flush()


def _parse_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    if len(date_str) >= 10:
        return date_str[:10]
    return None


def get_author_models(
    author: str,
    from_date: str,
    to_date: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Get recent models from an author/org on HuggingFace.

    Args:
        author: HuggingFace username or org (e.g. "meta-llama")
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        limit: Max results

    Returns:
        List of model info dicts
    """
    params = urlencode({
        "author": author,
        "sort": "lastModified",
        "direction": "-1",
        "limit": str(limit),
    })
    url = f"{HF_API}/models?{params}"

    try:
        response = http.get(url, timeout=30)
    except Exception as e:
        _log(f"Failed to fetch models for {author}: {e}")
        return []

    if not isinstance(response, list):
        return []

    models = []
    for model in response:
        # Prefer lastModified (most models are created once, updated often)
        created = _parse_date(model.get("createdAt"))
        modified = _parse_date(model.get("lastModified"))
        date = modified or created

        if not date:
            continue

        # Check if either created or modified falls in range
        in_range = (from_date <= date <= to_date)
        if not in_range and created and (from_date <= created <= to_date):
            date = created
            in_range = True
        if not in_range:
            continue

        downloads = model.get("downloads", 0) or 0
        likes = model.get("likes", 0) or 0

        models.append({
            "model_id": model.get("modelId", model.get("id", "")),
            "pipeline_tag": model.get("pipeline_tag", ""),
            "tags": model.get("tags", []),
            "downloads": downloads,
            "likes": likes,
            "date": date,
            "created": created,
            "modified": modified,
            "url": f"https://huggingface.co/{model.get('modelId', model.get('id', ''))}",
            "private": model.get("private", False),
            "library_name": model.get("library_name", ""),
        })

    _log(f"{author}: {len(models)} models in date range")
    return models


def get_trending_models(
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get trending models from HuggingFace."""
    params = urlencode({
        "sort": "trending",
        "direction": "-1",
        "limit": str(limit),
    })
    url = f"{HF_API}/models?{params}"

    try:
        response = http.get(url, timeout=30)
    except Exception as e:
        _log(f"Failed to fetch trending models: {e}")
        return []

    if not isinstance(response, list):
        return []
    return response


def search_models(
    query: str,
    from_date: str,
    to_date: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Search for models by keyword."""
    params = urlencode({
        "search": query,
        "sort": "lastModified",
        "direction": "-1",
        "limit": str(limit),
    })
    url = f"{HF_API}/models?{params}"

    try:
        response = http.get(url, timeout=30)
    except Exception as e:
        _log(f"Model search '{query}' failed: {e}")
        return []

    if not isinstance(response, list):
        return []

    models = []
    for model in response:
        created = _parse_date(model.get("createdAt"))
        modified = _parse_date(model.get("lastModified"))
        date = modified or created
        if date and (date < from_date or date > to_date):
            continue
        models.append(model)

    return models


def collect(
    entities: Dict[str, List[str]],
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> CollectionResult:
    """Collect HuggingFace model updates for tracked entities.

    Args:
        entities: Dict mapping entity name -> list of HF author/org names
            e.g. {"Meta AI": ["meta-llama"], "Google": ["google"]}
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_HUGGINGFACE)
    all_items = []
    limit = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])

    for entity_name, hf_authors in entities.items():
        result.entities_checked += 1
        entity_found = False

        for author in hf_authors:
            models = get_author_models(author, from_date, to_date, limit)

            for model in models:
                model_id = model.get("model_id", "")
                pipeline = model.get("pipeline_tag", "")
                downloads = model.get("downloads", 0)
                likes = model.get("likes", 0)
                tags = model.get("tags", [])

                tag_str = ", ".join(tags[:5]) if tags else ""
                summary_parts = []
                if pipeline:
                    summary_parts.append(f"Pipeline: {pipeline}")
                if downloads:
                    summary_parts.append(f"{downloads:,} downloads")
                if likes:
                    summary_parts.append(f"{likes} likes")
                if tag_str:
                    summary_parts.append(f"Tags: {tag_str}")

                all_items.append(TrackerItem(
                    id=f"HF-{model_id}",
                    title=model_id,
                    summary=" | ".join(summary_parts) if summary_parts else model_id,
                    entity=entity_name,
                    source=SOURCE_HUGGINGFACE,
                    source_url=model.get("url", f"https://huggingface.co/{model_id}"),
                    source_label=f"HuggingFace {author}",
                    date=model.get("date"),
                    date_confidence="high" if model.get("date") else "low",
                    raw_text=model_id,
                    engagement=Engagement(
                        likes=likes,
                        views=downloads,
                    ),
                    relevance=min(1.0, 0.5 + min(0.5, (downloads / 10000 + likes / 100))),
                ))
                entity_found = True

        if entity_found:
            result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} HF models from {result.entities_checked} entities")
    return result
