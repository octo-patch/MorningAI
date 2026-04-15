"""HuggingFace collector for morning-ai.

Monitors model/space/dataset updates via HuggingFace API.
New collector — no last30days equivalent.
"""

import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, quote

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_HUGGINGFACE

HF_API = "https://huggingface.co/api"

DEPTH_CONFIG = {"quick": 5, "default": 10, "deep": 20}


def _format_params(total: int) -> str:
    """Format parameter count to human-readable string (e.g. 31B, 600M)."""
    if total >= 1_000_000_000:
        val = total / 1_000_000_000
        return f"{val:.0f}B" if val == int(val) else f"{val:.1f}B"
    if total >= 1_000_000:
        val = total / 1_000_000
        return f"{val:.0f}M" if val == int(val) else f"{val:.1f}M"
    if total >= 1_000:
        val = total / 1_000
        return f"{val:.0f}K" if val == int(val) else f"{val:.1f}K"
    return str(total)


def _fetch_model_meta(model_id: str) -> Dict[str, str]:
    """Fetch rich metadata from HuggingFace model API.

    Returns dict with keys: params, arch, license, base_model (all optional).
    """
    url = f"{HF_API}/models/{quote(model_id, safe='/')}"
    try:
        data = http.get(url, timeout=15, retries=1)
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    result: Dict[str, str] = {}

    # Parameter count from safetensors
    safetensors = data.get("safetensors")
    if isinstance(safetensors, dict):
        total = safetensors.get("total")
        if isinstance(total, (int, float)) and total > 0:
            result["params"] = _format_params(int(total))

    # Architecture from config
    config = data.get("config")
    if isinstance(config, dict):
        archs = config.get("architectures")
        if isinstance(archs, list) and archs:
            # "Gemma3ForConditionalGeneration" -> "Gemma3"
            arch = archs[0]
            arch = re.sub(r'(For\w+|LMHead\w*|Model)$', '', arch)
            if arch:
                result["arch"] = arch
        if "arch" not in result:
            model_type = config.get("model_type")
            if model_type:
                result["arch"] = model_type

    # License and base_model from cardData
    card = data.get("cardData")
    if isinstance(card, dict):
        lic = card.get("license")
        if isinstance(lic, str) and lic:
            result["license"] = lic
        base = card.get("base_model")
        if isinstance(base, str) and base:
            result["base_model"] = base
        elif isinstance(base, list) and base:
            result["base_model"] = base[0] if isinstance(base[0], str) else ""

    return result


def _fetch_model_description(model_id: str) -> str:
    """Fetch model card description from HuggingFace README.

    Fetches the raw README.md and extracts the first meaningful paragraph
    after the YAML frontmatter. Falls back to empty string on failure.
    """
    url = f"https://huggingface.co/{model_id}/raw/main/README.md"
    try:
        text = http.get(url, timeout=10, retries=1, raw=True)
    except Exception:
        return ""

    if not isinstance(text, str) or len(text) < 20:
        return ""

    # Strip YAML frontmatter
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            text = text[end + 3:]

    # Find first substantial paragraph (skip blanks, headers, links, badges, emoji lines)
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith(("#", "|", "[", "!", "<", "-", "*", ">")):
            continue
        if line.startswith("```"):
            break
        # Skip lines starting with emoji (common promotional banners)
        if re.match(r'^[\U0001F000-\U0001FFFF\u2600-\u27BF\u2B50]', line):
            continue
        # Skip short lines and markdown link-only lines
        if len(line) < 50:
            continue
        if re.match(r'^\[.*\]\(.*\)$', line):
            continue
        # Found a real paragraph
        return line[:300]

    return ""


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

                # Metadata fallback summary
                tag_str = ", ".join(tags[:5]) if tags else ""
                meta_parts = []
                if pipeline:
                    meta_parts.append(f"Pipeline: {pipeline}")
                if downloads:
                    meta_parts.append(f"{downloads:,} downloads")
                if likes:
                    meta_parts.append(f"{likes} likes")
                if tag_str:
                    meta_parts.append(f"Tags: {tag_str}")
                fallback_summary = " | ".join(meta_parts) if meta_parts else model_id

                all_items.append(TrackerItem(
                    id=f"HF-{model_id}",
                    title=model_id,
                    summary=fallback_summary,
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

    # Enrich summaries with model card descriptions + technical metadata (concurrent)
    if all_items:
        _log(f"Fetching model details for {len(all_items)} models...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            desc_futures = {
                executor.submit(_fetch_model_description, item.title): ("desc", item)
                for item in all_items
            }
            meta_futures = {
                executor.submit(_fetch_model_meta, item.title): ("meta", item)
                for item in all_items
            }

            # Collect results keyed by item id
            descriptions: Dict[str, str] = {}
            metas: Dict[str, Dict[str, str]] = {}

            for future in as_completed({**desc_futures, **meta_futures}):
                if future in desc_futures:
                    _, item = desc_futures[future]
                    try:
                        descriptions[item.id] = future.result(timeout=20)
                    except Exception:
                        pass
                else:
                    _, item = meta_futures[future]
                    try:
                        metas[item.id] = future.result(timeout=20)
                    except Exception:
                        pass

            # Build enriched summaries
            for item in all_items:
                desc = descriptions.get(item.id, "")
                model_meta = metas.get(item.id, {})

                # Technical specs
                specs = []
                if model_meta.get("params"):
                    specs.append(f"{model_meta['params']} params")
                if model_meta.get("arch"):
                    specs.append(f"{model_meta['arch']} architecture")
                if model_meta.get("base_model"):
                    specs.append(f"based on {model_meta['base_model']}")
                if model_meta.get("license"):
                    specs.append(model_meta["license"])
                spec_str = ", ".join(specs)

                # Engagement metrics
                metrics = []
                if item.engagement.views:
                    metrics.append(f"{item.engagement.views:,} downloads")
                if item.engagement.likes:
                    metrics.append(f"{item.engagement.likes} likes")
                metric_str = " | ".join(metrics)

                # Assemble: description + specs + metrics
                parts = []
                if desc:
                    parts.append(desc[:200])
                if spec_str:
                    parts.append(spec_str)
                if metric_str:
                    parts.append(metric_str)

                if parts:
                    item.summary = ". ".join(parts)

    result.items = all_items
    _log(f"Collected {len(all_items)} HF models from {result.entities_checked} entities")
    return result
