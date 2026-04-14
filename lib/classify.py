"""Content type classifier for morning-ai.

Heuristic classifier that assigns content_type (product, model, benchmark,
financing) to TrackerItems based on source, title, and summary keywords.
Runs in the collect pipeline before scoring.
"""

import re
from typing import List

from .schema import (
    TrackerItem,
    TYPE_PRODUCT,
    TYPE_MODEL,
    TYPE_BENCHMARK,
    TYPE_FINANCING,
    SOURCE_ARXIV,
    SOURCE_HUGGINGFACE,
    SOURCE_GITHUB,
)

# Keyword patterns (case-insensitive) — checked against title + summary
_FINANCING_KEYWORDS = re.compile(
    r"(?i)\b("
    r"raises|raised|funding|funded|series\s+[a-f]|valuation|"
    r"acquisition|acquire[ds]?|merger|merg(?:ed|ing)|"
    r"ipo|invest(?:ment|ed|or)|"
    r"\$\d+[mb]\b|billion|million"
    r")\b"
)

_MODEL_KEYWORDS = re.compile(
    r"(?i)\b("
    r"model|weights|parameters|param|llm|"
    r"checkpoint|fine[- ]?tun|quantiz|"
    r"gguf|ggml|fp16|bf16|int[48]|"
    r"transformer|diffusion|"
    r"open[- ]?source[ds]?\s+(?:model|weight)|"
    r"vllm|ollama|lora|qlora|"
    r"embedding|tokenizer|"
    r"\d+[bB]\b"
    r")\b"
)

_BENCHMARK_KEYWORDS = re.compile(
    r"(?i)\b("
    r"benchmark|leaderboard|arena|eval(?:uation)?|"
    r"paper|arxiv|research|study|"
    r"ranking|score[ds]?|accuracy|"
    r"MMLU|GPQA|HumanEval|MATH|ARC|HellaSwag|"
    r"interpretab|alignment|safety"
    r")\b"
)

_PRODUCT_KEYWORDS = re.compile(
    r"(?i)\b("
    r"feature|launch(?:ed|es)?|changelog|"
    r"version\s|v\d+\.\d+|release[ds]?|"
    r"cli|sdk|api|app|plugin|extension|"
    r"update[ds]?|upgrade[ds]?|"
    r"pricing|plan|tier|"
    r"beta|preview|ga\b|"
    r"dashboard|interface|ui|ux"
    r")\b"
)


def _classify_one(item: TrackerItem) -> str:
    """Classify a single item's content type."""
    text = f"{item.title} {item.summary}"

    # Rule 1: financing keywords (highest priority — rare and distinctive)
    if _FINANCING_KEYWORDS.search(text):
        return TYPE_FINANCING

    # Rule 2: arXiv source → benchmark/research
    if item.source == SOURCE_ARXIV:
        return TYPE_BENCHMARK

    # Rule 3: HuggingFace source → model
    if item.source == SOURCE_HUGGINGFACE:
        return TYPE_MODEL

    # Rule 4: benchmark keywords
    if _BENCHMARK_KEYWORDS.search(text):
        return TYPE_BENCHMARK

    # Rule 5: model keywords
    if _MODEL_KEYWORDS.search(text):
        return TYPE_MODEL

    # Rule 6: product keywords or GitHub source (tool releases)
    if _PRODUCT_KEYWORDS.search(text):
        return TYPE_PRODUCT

    if item.source == SOURCE_GITHUB:
        return TYPE_PRODUCT

    # Rule 7: fallback
    return TYPE_PRODUCT


def classify_items(items: List[TrackerItem]) -> List[TrackerItem]:
    """Assign content_type to items that don't already have one.

    Args:
        items: List of TrackerItems from collectors

    Returns:
        Same list with content_type populated
    """
    for item in items:
        if not item.content_type:
            item.content_type = _classify_one(item)
    return items
