"""Entity registry for morning-ai.

Loads 80+ tracked entities from ``entities/*.md`` at import time.
Custom entities are merged from:
    1. CUSTOM_ENTITIES_DIR env var
    2. ~/.config/morning-ai/entities/
    3. {project_root}/entities/custom/
"""

from lib.custom_entities import load_builtin_entities, merge_into_registries

# Load built-in entities from entities/*.md
_builtin = load_builtin_entities()

X_HANDLES = _builtin["x_handles"]
GITHUB_SOURCES = _builtin["github_sources"]
HUGGINGFACE_AUTHORS = _builtin["huggingface_authors"]
ARXIV_QUERIES = _builtin["arxiv_queries"]
WEB_QUERIES = _builtin["web_queries"]
REDDIT_KEYWORDS = _builtin["reddit_keywords"]
HN_KEYWORDS = _builtin["hn_keywords"]

# Merge custom entities on top
merge_into_registries(
    X_HANDLES,
    GITHUB_SOURCES,
    HUGGINGFACE_AUTHORS,
    ARXIV_QUERIES,
    WEB_QUERIES,
    REDDIT_KEYWORDS,
    HN_KEYWORDS,
)
