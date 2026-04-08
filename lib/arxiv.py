"""arXiv collector for morning-ai.

Searches arXiv papers via the Atom/XML API (free, no auth).
New collector — no last30days equivalent.
"""

import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, quote

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_ARXIV

ARXIV_API = "http://export.arxiv.org/api/query"

DEPTH_CONFIG = {"quick": 10, "default": 25, "deep": 50}

# arXiv categories for AI
AI_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.MA"]

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[arXiv] {msg}\n")
        sys.stderr.flush()


def _parse_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    if len(date_str) >= 10:
        return date_str[:10]
    return None


def _clean_text(text: str) -> str:
    """Clean arXiv abstract text."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def search_papers(
    query: str,
    from_date: str,
    to_date: str,
    categories: Optional[List[str]] = None,
    max_results: int = 25,
) -> List[Dict[str, Any]]:
    """Search arXiv papers via Atom API.

    Args:
        query: Search query (author, title, abstract keywords)
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        categories: arXiv categories to filter (e.g. ["cs.CL", "cs.LG"])
        max_results: Max papers to return

    Returns:
        List of paper dicts
    """
    # Build arXiv search query
    search_parts = []
    if query:
        search_parts.append(f"all:{query}")
    if categories:
        cat_query = " OR ".join(f"cat:{cat}" for cat in categories)
        search_parts.append(f"({cat_query})")

    search_query = " AND ".join(search_parts) if search_parts else query

    params = urlencode({
        "search_query": search_query,
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API}?{params}"

    try:
        xml_text = http.get(url, timeout=30, raw=True)
    except Exception as e:
        _log(f"arXiv search '{query}' failed: {e}")
        return []

    # Parse XML
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        _log(f"Failed to parse arXiv XML: {e}")
        return []

    papers = []
    for entry in root.findall(f"{ATOM_NS}entry"):
        title_el = entry.find(f"{ATOM_NS}title")
        summary_el = entry.find(f"{ATOM_NS}summary")
        published_el = entry.find(f"{ATOM_NS}published")
        updated_el = entry.find(f"{ATOM_NS}updated")

        title = _clean_text(title_el.text) if title_el is not None and title_el.text else ""
        abstract = _clean_text(summary_el.text) if summary_el is not None and summary_el.text else ""
        published = _parse_date(published_el.text if published_el is not None else None)
        updated = _parse_date(updated_el.text if updated_el is not None else None)

        date = published or updated
        if date and (date < from_date or date > to_date):
            continue

        # Get paper URL
        paper_url = ""
        pdf_url = ""
        for link in entry.findall(f"{ATOM_NS}link"):
            href = link.get("href", "")
            link_type = link.get("type", "")
            title_attr = link.get("title", "")
            if title_attr == "pdf" or "pdf" in href:
                pdf_url = href
            elif link_type == "text/html" or (href and "abs" in href):
                paper_url = href
            elif not paper_url and href:
                paper_url = href

        # Get authors
        authors = []
        for author_el in entry.findall(f"{ATOM_NS}author"):
            name_el = author_el.find(f"{ATOM_NS}name")
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        # Get categories
        cats = []
        for cat_el in entry.findall("{http://arxiv.org/schemas/atom}primary_category"):
            term = cat_el.get("term", "")
            if term:
                cats.append(term)
        for cat_el in entry.findall(f"{ATOM_NS}category"):
            term = cat_el.get("term", "")
            if term and term not in cats:
                cats.append(term)

        # Extract arXiv ID from URL
        arxiv_id = ""
        if paper_url:
            match = re.search(r"(\d{4}\.\d{4,5})(v\d+)?$", paper_url)
            if match:
                arxiv_id = match.group(1)

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "date": date,
            "published": published,
            "updated": updated,
            "url": paper_url,
            "pdf_url": pdf_url,
            "categories": cats,
        })

    _log(f"arXiv '{query}': {len(papers)} papers in date range")
    return papers


def collect(
    entities: Dict[str, List[str]],
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> CollectionResult:
    """Collect arXiv papers for tracked entities.

    Args:
        entities: Dict mapping entity name -> list of search queries
            e.g. {"OpenAI": ["OpenAI"], "Anthropic": ["Anthropic"]}
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_ARXIV)
    all_items = []
    max_results = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])

    for entity_name, queries in entities.items():
        result.entities_checked += 1
        entity_found = False

        for query in queries:
            papers = search_papers(
                query, from_date, to_date,
                categories=AI_CATEGORIES,
                max_results=max_results,
            )

            for paper in papers:
                authors = paper.get("authors", [])
                author_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    author_str += f" et al. ({len(authors)} authors)"

                cats = paper.get("categories", [])
                cat_str = ", ".join(cats[:3])

                abstract = paper.get("abstract", "")
                summary = f"By {author_str}. {abstract[:200]}" if author_str else abstract[:300]

                all_items.append(TrackerItem(
                    id=f"ARXIV-{paper.get('arxiv_id', '')}",
                    title=paper.get("title", ""),
                    summary=summary,
                    entity=entity_name,
                    source=SOURCE_ARXIV,
                    source_url=paper.get("url", ""),
                    source_label=f"arXiv [{cat_str}]" if cat_str else "arXiv",
                    date=paper.get("date"),
                    date_confidence="high" if paper.get("date") else "low",
                    raw_text=abstract,
                    relevance=0.7,
                ))
                entity_found = True

        if entity_found:
            result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} arXiv papers from {result.entities_checked} entities")
    return result
