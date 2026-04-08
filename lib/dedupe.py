"""Near-duplicate detection for morning-ai.

Adapted from last30days dedupe.py.
Supports within-source dedup and cross-source linking.
"""

import re
from typing import List, Set, Tuple

from .schema import TrackerItem

# Stopwords for token-based matching
STOPWORDS = frozenset({
    "the", "a", "an", "to", "for", "how", "is", "in", "of", "on",
    "and", "with", "from", "by", "at", "this", "that", "it", "my",
    "your", "i", "me", "we", "you", "what", "are", "do", "can",
    "its", "be", "or", "not", "no", "so", "if", "but", "about",
    "all", "just", "get", "has", "have", "was", "will", "new",
    "ai", "model", "release", "update", "now", "available",
})


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_ngrams(text: str, n: int = 3) -> Set[str]:
    """Get character n-grams from text."""
    text = normalize_text(text)
    if len(text) < n:
        return {text}
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def get_item_text(item: TrackerItem) -> str:
    """Get comparable text from a TrackerItem."""
    if item.title:
        return item.title
    return item.raw_text[:150]


def _tokenize(text: str) -> Set[str]:
    """Tokenize text for token-level Jaccard."""
    words = re.sub(r"[^\w\s]", " ", text.lower()).split()
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _token_jaccard(text_a: str, text_b: str) -> float:
    """Token-level Jaccard similarity."""
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union else 0.0


def hybrid_similarity(text_a: str, text_b: str) -> float:
    """Hybrid similarity: max of char-trigram Jaccard and token Jaccard."""
    trigram_sim = jaccard_similarity(get_ngrams(text_a), get_ngrams(text_b))
    token_sim = _token_jaccard(text_a, text_b)
    return max(trigram_sim, token_sim)


def find_duplicates(
    items: List[TrackerItem],
    threshold: float = 0.7,
) -> List[Tuple[int, int]]:
    """Find near-duplicate pairs by Jaccard similarity.

    Args:
        items: List of items to check
        threshold: Similarity threshold (0-1)

    Returns:
        List of (i, j) index pairs where items are similar
    """
    duplicates = []
    ngrams = [get_ngrams(get_item_text(item)) for item in items]

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            similarity = jaccard_similarity(ngrams[i], ngrams[j])
            if similarity >= threshold:
                duplicates.append((i, j))

    return duplicates


def dedupe_items(
    items: List[TrackerItem],
    threshold: float = 0.7,
) -> List[TrackerItem]:
    """Remove near-duplicates, keeping highest-scored item.

    Args:
        items: List of items (should be pre-sorted by importance desc)
        threshold: Similarity threshold

    Returns:
        Deduplicated items
    """
    if len(items) <= 1:
        return items

    dup_pairs = find_duplicates(items, threshold)

    to_remove = set()
    for i, j in dup_pairs:
        if items[i].importance >= items[j].importance:
            to_remove.add(j)
        else:
            to_remove.add(i)

    return [item for idx, item in enumerate(items) if idx not in to_remove]


def dedupe_by_source(items: List[TrackerItem], threshold: float = 0.7) -> List[TrackerItem]:
    """Deduplicate items within each source separately.

    More efficient than global dedup for large item sets.

    Args:
        items: All collected items
        threshold: Similarity threshold

    Returns:
        Deduplicated items
    """
    by_source = {}
    for item in items:
        by_source.setdefault(item.source, []).append(item)

    result = []
    for source, source_items in by_source.items():
        source_items.sort(key=lambda x: x.importance, reverse=True)
        deduped = dedupe_items(source_items, threshold)
        result.extend(deduped)

    return result


def cross_source_link(
    items: List[TrackerItem],
    threshold: float = 0.40,
) -> List[TrackerItem]:
    """Link similar items across different sources.

    Uses hybrid similarity (char-trigram + token Jaccard) for cross-source
    matching. Adds bidirectional cross_refs when similarity exceeds threshold.

    Also considers entity matching: items about the same entity get a
    similarity boost for more accurate cross-referencing.

    Args:
        items: All items from all sources
        threshold: Similarity threshold for cross-linking

    Returns:
        Items with cross_refs populated
    """
    if len(items) <= 1:
        return items

    # Pre-compute texts for comparison (truncate long texts for fairness)
    texts = []
    for item in items:
        text = get_item_text(item)
        if item.source == "x":
            text = text[:100]
        texts.append(text)

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            # Skip same-source comparisons
            if items[i].source == items[j].source:
                continue

            similarity = hybrid_similarity(texts[i], texts[j])

            # Entity match bonus: same entity increases likelihood of cross-ref
            if items[i].entity and items[i].entity == items[j].entity:
                similarity += 0.1

            if similarity >= threshold:
                if items[j].id not in items[i].cross_refs:
                    items[i].cross_refs.append(items[j].id)
                if items[i].id not in items[j].cross_refs:
                    items[j].cross_refs.append(items[i].id)

    return items
