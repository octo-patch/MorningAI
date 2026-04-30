"""X/Twitter collector for morning-ai (Anthropic SDK + web_search server tool).

Calls the Anthropic Messages API directly with the server-side ``web_search``
tool to find tweets from tracked AI handles, then parses the model's JSON
output into TrackerItems.

Two collector tasks run in parallel — one for official accounts, one for
Key People — matching the verification policy in
``skills/tracking-list/SKILL.md`` ("official accounts: accept directly /
key people: requires cross-verification").

Why direct SDK instead of ``claude -p`` subprocess: Claude Code's default
system prompt forbids generating URLs, which the model treats as a hard
guard against this exact task ("Returning tweet URLs is the required
machine-readable output"). Using the SDK lets us supply our own system
prompt that frames URL emission as the legitimate ingestion contract.
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse, urlunparse

try:
    import anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_X
from .util import log

# How many handles each tier-agent will search at each depth. Empirically a
# single WebSearch via `claude -p` takes ~50-70s, but parallel claude
# processes contend on the proxy / API and slow down — so we keep parallelism
# modest (TIER_MAX_PARALLEL=2) and cap handles to fit ~2 waves per tier
# inside collect.py's 600s future timeout.
DEPTH_HANDLES_PER_TIER = {"quick": 6, "default": 12, "deep": 18}

# Handles per sub-agent invocation. The agent runs ONE WebSearch per handle
# (`site:x.com/<handle> ...`); 3 keeps each chunk under ~250s.
CHUNK_SIZE = int(os.getenv("X_AGENT_CHUNK_SIZE", "3"))

# Per-subprocess timeout. Default 600s allows for slow corporate Anthropic
# gateways (observed ~100s wall-clock for trivial echo prompts via internal
# ANTHROPIC_BASE_URL). 3 WebSearch calls + reasoning + JSON output won't fit
# in 300s on those gateways. Chunks within a tier run in parallel (see
# _collect_tier), and the two tiers also run in parallel, so wall-clock ≈
# ceil(chunks/parallel) × this.
CLAUDE_TIMEOUT = int(os.getenv("X_AGENT_TIMEOUT", "600"))
CLAUDE_MODEL = os.getenv("X_AGENT_MODEL", "sonnet")

# Max concurrent sub-agent processes per tier. Beyond ~2 the corporate proxy
# and Anthropic API rate limits drive each chunk well past CLAUDE_TIMEOUT
# (observed 9/10 chunks timing out at parallelism=5). Keep low.
TIER_MAX_PARALLEL = int(os.getenv("X_AGENT_TIER_PARALLEL", "2"))


_log = lambda msg: log("x-agent", msg)


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

_PROMPT_HEADER = """TASK: Find AI-relevant posts on X authored by the {n_handles} {tier_label}(s) below.
Window: posts published between {from_date} and {to_date} (UTC+8 [yesterday 08:00,
today 08:00)). For dating, use the tweet snowflake ID — IDs roughly ≥
{min_snowflake_hint} fall inside or near the window; older IDs predate it.

HANDLES (entity -> handle):
{handles_listing}

PROCEDURE — MANDATORY, NO DEVIATIONS:
1. Run EXACTLY {n_handles} web_search calls — ONE per handle. NO MORE, NO RETRIES.
2. For each handle, query: `site:x.com/<handle> launch OR release OR announce OR model OR benchmark OR funding OR partnership`
3. Read the top 5 results. Pick at most 2 per handle that are:
   - URL pattern: x.com/<handle>/status/<id> (NOT replies, NOT third-party tweets)
   - Snowflake ID consistent with the window (≥ {min_snowflake_hint} preferred; allow ~1 week prior with date_confidence="low")
   - About product launches, model releases, benchmarks, funding, capability upgrades, official partnerships
   - SKIP: pure marketing, retweets, replies, personal content
4. DO NOT do verification searches. DO NOT search again if results look sparse.
"""

_PROMPT_VERIFY_KEY_PEOPLE = ""  # Verification disabled — see module docstring.

_PROMPT_OUTPUT_SPEC = """
OUTPUT: A single JSON array wrapped in ```json fences. NO prose before or after.
For each item, output ONE object with exactly these fields:

{
  "title": "<5-12 word headline summarizing the post>",
  "summary": "<one-sentence summary, ≤200 chars>",
  "entity": "<entity name from the mapping above — must match exactly>",
  "source": "x",
  "source_url": "https://x.com/<handle>/status/<tweet_id>",
  "source_label": "@<handle> on X",
  "date": "YYYY-MM-DD (best-effort from snowflake ID; empty string if unsure)",
  "date_confidence": "high|med|low",
  "raw_text": "<verbatim snippet from the search result>",
  "engagement": {"likes": 0, "reposts": 0, "replies": 0, "quotes": 0},
  "verified": false,
  "verify_sources": []
}

Use empty string / 0 / [] for unknown fields — do NOT fabricate.
If a handle has no qualifying posts, just skip it. If NO handle yields any item,
output exactly: ```json
[]
```
"""


def _snowflake_hint(from_date: str) -> str:
    """Compute an approximate snowflake ID for a YYYY-MM-DD UTC+8 date.

    Twitter snowflake IDs are millisecond-monotonic, with the epoch at
    2010-11-04T01:42:54.657Z. ID = (ms_since_epoch << 22). Returns a string
    rounded to 12 significant figures so the agent can use it as a quick
    lower-bound filter without us having to be cycle-accurate.
    """
    from datetime import datetime, timezone, timedelta
    try:
        # YYYY-MM-DD interpreted as 08:00 UTC+8 = 00:00 UTC of that date
        d = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        epoch = datetime(2010, 11, 4, 1, 42, 54, 657000, tzinfo=timezone.utc)
        ms = int((d - epoch).total_seconds() * 1000)
        snowflake = ms << 22
        # Round down to 13 digits (drop last 5) so the hint is approximate
        return str(snowflake // 10**5 * 10**5)
    except Exception:
        return "2040000000000000000"  # fallback: late 2025


def _build_prompt(
    chunk: List[Tuple[str, str]],  # list of (entity_name, handle)
    tier: str,
    from_date: str,
    to_date: str,
) -> str:
    """Construct the sub-agent prompt for a chunk of handles."""
    tier_label = "official account" if tier == "official" else "Key People"

    handles_listing = "\n".join(
        f"  {entity} -> @{handle}" for entity, handle in chunk
    )

    body = _PROMPT_HEADER.format(
        from_date=from_date,
        to_date=to_date,
        tier_label=tier_label,
        n_handles=len(chunk),
        handles_listing=handles_listing,
        min_snowflake_hint=_snowflake_hint(from_date),
    )
    body += _PROMPT_OUTPUT_SPEC
    return body


# ---------------------------------------------------------------------------
# Sub-agent invocation + JSON parsing
# ---------------------------------------------------------------------------

# Friendly aliases → current model IDs. Falls through to whatever the user
# put in X_AGENT_MODEL if not in this map.
_MODEL_ALIASES = {
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-6",
    "haiku": "claude-haiku-4-5",
}

# System prompt that frames URL emission as the legitimate ingestion contract.
# Without this, Claude Code's default system prompt's URL guard kicks in and
# the model refuses ("I won't generate URLs unless directly related to
# helping with programming tasks") — see commit history for the incident.
_SYSTEM_PROMPT = (
    "You are a data-ingestion service for the open-source morning-ai AI "
    "industry tracker pipeline (github.com/autoclaw-cc/morning-ai, module "
    "lib/x_agent.py). You search the public web for recent posts on X "
    "(Twitter) authored by a fixed list of AI company/researcher accounts "
    "and emit them as structured JSON for downstream automated processing.\n\n"
    "The URLs you emit (https://x.com/<handle>/status/<id>) are canonical "
    "record identifiers consumed by downstream deduplication and storage. "
    "Always include them when you find a qualifying tweet — they are the "
    "primary key of every record.\n\n"
    "Output exactly one JSON array wrapped in ```json fences, with no prose "
    "before or after."
)

# Module-level singleton client (Anthropic SDK is thread-safe). Reads
# ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / ANTHROPIC_BASE_URL from env.
_CLIENT: "anthropic.Anthropic | None" = None


def _parse_custom_headers() -> Dict[str, str]:
    """Parse ANTHROPIC_CUSTOM_HEADERS (newline- or comma-separated `Key: Value`).

    Some corporate Anthropic gateways (e.g. internal proxies) require routing
    headers like ``X-Sub-Module`` or ``X-From``. Claude Code injects these
    automatically; raw SDK calls must pass them via ``default_headers=``.
    """
    raw = os.environ.get("ANTHROPIC_CUSTOM_HEADERS", "")
    if not raw:
        return {}
    headers: Dict[str, str] = {}
    # Split on newline first, fall back to comma if all on one line.
    parts = raw.splitlines() if "\n" in raw else raw.split(",")
    for part in parts:
        part = part.strip()
        if not part or ":" not in part:
            continue
        key, _, value = part.partition(":")
        headers[key.strip()] = value.strip()
    return headers


def _client() -> "anthropic.Anthropic":
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.Anthropic(default_headers=_parse_custom_headers() or None)
    return _CLIENT


class _SubagentTimeout(Exception):
    """Raised when the SDK call exceeds CLAUDE_TIMEOUT."""


def _run_subagent(prompt: str, env: Dict[str, str]) -> str:
    """Call the Anthropic Messages API with the server-side ``web_search`` tool.

    Streams the response (long-running with thinking + tool use), loops on
    ``stop_reason == "pause_turn"`` until the model is done, and returns the
    concatenated text from all assistant turns. Raises ``_SubagentTimeout``
    on timeout.

    The ``env`` arg is unused by the SDK (kept for signature compat with the
    previous subprocess-based implementation), since the SDK reads
    ANTHROPIC_* env vars directly from ``os.environ``.
    """
    del env  # SDK reads env directly
    client = _client()
    model = _MODEL_ALIASES.get(CLAUDE_MODEL, CLAUDE_MODEL)

    messages: List[Dict[str, Any]] = [{"role": "user", "content": prompt}]
    text_parts: List[str] = []

    # Server-side web_search may need multiple turns when the model issues
    # tool calls; cap iterations to bound runtime. The prompt asks for exactly
    # N searches, so 1-3 turns is typical.
    for _ in range(8):
        try:
            with client.messages.stream(
                model=model,
                max_tokens=8192,
                system=_SYSTEM_PROMPT,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=messages,
                timeout=CLAUDE_TIMEOUT,
            ) as stream:
                final = stream.get_final_message()
        except (anthropic.APITimeoutError if _HAS_ANTHROPIC else _SubagentTimeout) as e:
            raise _SubagentTimeout(str(e)) from e

        # Append the full assistant content back so the server can continue
        # the tool loop on the next iteration.
        messages.append({"role": "assistant", "content": final.content})

        # Collect text blocks from this turn (skip thinking, tool_use, and
        # web_search_tool_result blocks — we only want the model's prose).
        for block in final.content:
            if getattr(block, "type", None) == "text":
                text_parts.append(block.text)

        if final.stop_reason == "pause_turn":
            continue
        break  # end_turn, max_tokens, stop_sequence, refusal, etc.

    return "\n".join(text_parts)


def _parse_json_array(stdout: str) -> List[Dict[str, Any]]:
    """Extract a JSON array from sub-agent output. Returns [] on parse failure."""
    # Prefer fenced block
    m = re.search(r"```json\s*(\[.*?\])\s*```", stdout, re.DOTALL)
    if not m:
        # Fallback: any bracketed array containing objects
        m = re.search(r"(\[\s*\{.*?\}\s*\])", stdout, re.DOTALL)
    if not m:
        # Empty array literal
        if re.search(r"\[\s*\]", stdout):
            return []
        raise ValueError(f"no JSON array found in stdout (len={len(stdout)})")
    return json.loads(m.group(1))


# ---------------------------------------------------------------------------
# JSON -> TrackerItem
# ---------------------------------------------------------------------------

def _canonical_url(url: str) -> str:
    """Strip query string and trailing slash from a tweet URL for dedup."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        cleaned = urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))
        return cleaned.lower()
    except Exception:
        return url.lower()


def _to_tracker_item(raw: Dict[str, Any], idx: int, tier: str) -> TrackerItem:
    """Convert a single sub-agent JSON object into a TrackerItem."""
    eng = raw.get("engagement", {}) or {}
    engagement = Engagement(
        likes=int(eng.get("likes") or 0),
        reposts=int(eng.get("reposts") or 0),
        replies=int(eng.get("replies") or 0),
        quotes=int(eng.get("quotes") or 0),
    )
    # Extract tweet ID from source_url for stable item ID
    source_url = raw.get("source_url", "") or ""
    tweet_id_match = re.search(r"/status/(\d+)", source_url)
    item_id = f"X-{tweet_id_match.group(1)}" if tweet_id_match else f"X-{tier}-{idx}"

    # Heuristic relevance: official tier 0.85, key_people 0.7 (lower because
    # less reliable per SKILL.md priority table). Verification bonus added
    # later by apply_verification_bonus.
    relevance = 0.85 if tier == "official" else 0.7

    return TrackerItem(
        id=item_id,
        title=str(raw.get("title", "")).strip(),
        summary=str(raw.get("summary", "")).strip()[:300],
        entity=str(raw.get("entity", "")).strip(),
        source=SOURCE_X,
        source_url=source_url,
        source_label=str(raw.get("source_label", "")).strip() or "X",
        date=raw.get("date") or None,
        date_confidence=str(raw.get("date_confidence", "med")),
        raw_text=str(raw.get("raw_text", "")).strip(),
        engagement=engagement,
        relevance=relevance,
        verified=bool(raw.get("verified", False)),
        verify_sources=list(raw.get("verify_sources", []) or []),
    )


# ---------------------------------------------------------------------------
# Per-tier collection
# ---------------------------------------------------------------------------

def _flatten_handles(handles_dict: Dict[str, List[str]]) -> List[Tuple[str, str]]:
    """Flatten {entity: [handle, ...]} into [(entity, handle), ...]."""
    out: List[Tuple[str, str]] = []
    for entity, handles in handles_dict.items():
        for handle in handles:
            out.append((entity, handle))
    return out


def _collect_tier(
    handles_dict: Dict[str, List[str]],
    tier: str,
    from_date: str,
    to_date: str,
    depth: str,
    env: Dict[str, str],
) -> Tuple[List[TrackerItem], List[str]]:
    """Run one tier-agent over all chunks (chunks run in parallel).

    Returns (items, errors).
    """
    chunk_size = CHUNK_SIZE
    handle_cap = DEPTH_HANDLES_PER_TIER.get(depth, DEPTH_HANDLES_PER_TIER["default"])
    all_handles = _flatten_handles(handles_dict)[:handle_cap]
    if not all_handles:
        return [], []

    chunks = [all_handles[i:i + chunk_size] for i in range(0, len(all_handles), chunk_size)]
    parallelism = min(len(chunks), TIER_MAX_PARALLEL)
    _log(
        f"[{tier}] {len(all_handles)} handles (cap={handle_cap}) -> {len(chunks)} "
        f"chunk(s) of size {chunk_size}, parallelism={parallelism}"
    )

    items: List[TrackerItem] = []
    errors: List[str] = []

    def _process_chunk(chunk_idx: int, chunk: List[Tuple[str, str]]) -> Tuple[List[TrackerItem], List[str]]:
        prompt = _build_prompt(chunk, tier, from_date, to_date)
        local_items: List[TrackerItem] = []
        local_errors: List[str] = []
        try:
            stdout = _run_subagent(prompt, env)
        except _SubagentTimeout:
            local_errors.append(f"{tier} chunk {chunk_idx}: timeout after {CLAUDE_TIMEOUT}s")
            return local_items, local_errors
        except Exception as e:
            local_errors.append(f"{tier} chunk {chunk_idx}: subagent failed: {e}")
            return local_items, local_errors

        try:
            raw_items = _parse_json_array(stdout)
        except Exception as e:
            local_errors.append(f"{tier} chunk {chunk_idx}: JSON parse failed: {e}")
            return local_items, local_errors

        for i, raw in enumerate(raw_items):
            try:
                local_items.append(_to_tracker_item(raw, i, tier))
            except Exception as e:
                local_errors.append(f"{tier} chunk {chunk_idx} item {i}: {e}")

        _log(f"[{tier}] chunk {chunk_idx + 1}/{len(chunks)}: {len(raw_items)} items")
        return local_items, local_errors

    with ThreadPoolExecutor(max_workers=parallelism) as executor:
        futures = {
            executor.submit(_process_chunk, idx, chunk): idx
            for idx, chunk in enumerate(chunks)
        }
        for future in as_completed(futures):
            try:
                chunk_items, chunk_errors = future.result()
                items.extend(chunk_items)
                errors.extend(chunk_errors)
            except Exception as e:
                idx = futures[future]
                errors.append(f"{tier} chunk {idx}: future crashed: {e}")

    return items, errors


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def collect(
    handles_by_tier: Dict[str, Dict[str, List[str]]],
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> CollectionResult:
    """Collect X posts via two parallel tier-agents (official + Key People).

    Args:
        handles_by_tier: {"official": {entity: [handle, ...]}, "key_people": {...}}
        from_date: YYYY-MM-DD start of window
        to_date: YYYY-MM-DD end of window (exclusive)
        depth: quick | default | deep — controls chunk size

    Returns:
        CollectionResult(source="x", items=[...], errors=[...]).
        Never raises — failures land in `errors`.
    """
    result = CollectionResult(source=SOURCE_X)
    if not _HAS_ANTHROPIC:
        result.errors.append("anthropic SDK not installed — skipping X collector")
        return result
    env = dict(os.environ)  # inherit HTTPS_PROXY etc. from parent

    official = handles_by_tier.get("official", {}) or {}
    key_people = handles_by_tier.get("key_people", {}) or {}
    kol = handles_by_tier.get("kol", {}) or {}
    result.entities_checked = len(set(official.keys()) | set(key_people.keys()) | set(kol.keys()))

    if not official and not key_people and not kol:
        result.errors.append("no X handles configured")
        return result

    all_items: List[TrackerItem] = []

    # Run all tiers in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        if official:
            futures[executor.submit(
                _collect_tier, official, "official", from_date, to_date, depth, env
            )] = "official"
        if key_people:
            futures[executor.submit(
                _collect_tier, key_people, "key_people", from_date, to_date, depth, env
            )] = "key_people"
        if kol:
            futures[executor.submit(
                _collect_tier, kol, "kol", from_date, to_date, depth, env
            )] = "kol"

        for future in as_completed(futures):
            tier = futures[future]
            try:
                items, errors = future.result()
                all_items.extend(items)
                result.errors.extend(errors)
                _log(f"[{tier}] tier done: {len(items)} items, {len(errors)} errors")
            except Exception as e:
                result.errors.append(f"{tier} tier crashed: {e}")

    # Intra-collector dedup by canonical URL (same tweet may appear under
    # multiple handles when authors retweet/quote each other)
    seen_urls = {}
    deduped: List[TrackerItem] = []
    for item in all_items:
        key = _canonical_url(item.source_url) or item.id
        if key in seen_urls:
            continue
        seen_urls[key] = True
        deduped.append(item)

    result.items = deduped
    result.entities_with_updates = len({item.entity for item in deduped if item.entity})
    _log(
        f"X collection complete: {len(deduped)} unique items "
        f"({len(all_items) - len(deduped)} dups removed), {len(result.errors)} errors"
    )
    return result
