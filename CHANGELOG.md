# Changelog

## [1.4.2] - 2026-04-21

### New Features
- **Per-category social images for the X channel**: `skills/gen-social/templates/x/briefing.md` now emits a separate 16:9 infographic for each content category (Model, Product, Benchmark, Funding) alongside the cover, when that category has ≥1 qualifying item. Per-category images include all qualifying items (not the cover's top-N cap) and use a date-less header so they're reusable. The `---media---` block keys filenames by role (`cover:`, `model:`, `product:`, …) so downstream uploaders can attach them in order or skip empty roles.
- **Pluggable image generation provider**: `lib/image_gen.py` adds `IMAGE_GEN_PROVIDER_PATH` — point it at any Python file that exports `generate(prompt, output_path, config, **kwargs)` and the dispatcher will load and invoke it instead of (or in addition to) the built-in providers. Lets users plug in proprietary or experimental backends without forking the repo.
- **X handle tier registry**: `lib/entities.py` now exposes `X_HANDLES_OFFICIAL` and `X_HANDLES_KEY_PEOPLE` alongside the flat `X_HANDLES`, populated by the entity loader from the `Key People` sections vs. the official `X Account` columns. `lib/x_agent.py` (the in-process X collector introduced in 1.4.1) consumes these so each tier-agent runs the right verification policy. KOL tabular files default to the official tier; custom-entity X handles default to the official tier.
- **X collector switched to Anthropic SDK + `web_search` server tool** (`lib/x_agent.py`): replaces the previous `claude -p` subprocess so the URL-guard system prompt no longer blocks ingestion. Custom system prompt frames URL emission as the legitimate ingestion contract; loops on `pause_turn` until done; forwards `ANTHROPIC_CUSTOM_HEADERS` for corporate gateways. End-to-end depth=quick over 12 handles: 33.7s wall clock, 0 errors (previous: 600s timeout on 4/4 chunks).

### Improvements
- **Xiaohongshu news-briefing tone overhaul**: `skills/gen-social/templates/xiaohongshu/news-briefing.md` rewritten end-to-end. `default_items` 8 → 5, `image_style` newspaper → classic, hashtags 3-5 → 5-10, title format from `⚡AI速报｜M.D` to news-desk style `📰AI快讯｜N条要闻速览`. Body shifts from telegraph-style `｜`-separated lines to proper news-briefing paragraphs.
- **Glassmorphism palette retuned to warm tones** (`skills/gen-infographic/scripts/styles.py`): cool lavender→rose gradient replaced with apricot→cream + brown/taupe accents. Higher contrast against typical XHS feed colors and less Material Design-ish.
- **Reddit collector now logs network errors**: `lib/reddit.py:_fetch_json` previously swallowed every URLError / OSError / JSONDecodeError and returned None — daily runs showed "0 items, 0 errors" with no diagnostic clue. It now logs the failing URL and exception class.

### Bug Fixes
- **MiniMax image API parameter rename** (`lib/image_gen.py`): `response_format` value `b64_json` → `base64`. The API renamed the value silently; old runs were getting empty responses.
- **Cache key collision between full and partial source runs** (`lib/cache.py`): `get_cache_key()` now accepts an optional `extra` discriminator. Used by `collect.py`'s `--skip` change so a `--skip reddit` run doesn't read a previous full-source cache slot for the same date.
- **Daily-run manifest artifacts polluting `git status`**: added `/manifest_*.json` to `.gitignore` so `manifest_2026-MM-DD.json` and `manifest_single_*.json` no longer show as untracked.

### Internal
- **Extracted IPv4 fallback into `lib/net.py`**: `force_ipv4_only()` context manager + `is_ipv6_unreachable()` predicate. Reused from `lib/email_sender.py` (was the original implementation, now refactored to call the shared helpers) and applied to `lib/http.py` (arxiv / Hacker News / GitHub / HuggingFace) and `lib/reddit.py`. Completes the collector-side IPv4 fallback originally promised in 1.3.0.
- **arXiv 3-day default lookback** (`lib/arxiv.py`): `ARXIV_LOOKBACK_DAYS=3` widens the strict 1-day window. Override to `1` to restore the previous behavior. Documented in `README.md`.

## [1.4.1] - 2026-04-21

### Bug Fixes
- **arXiv silently dropped from daily runs**: Diagnosed via cache-key reverse-lookup — `~/.cache/morning-ai/c3201fd7243a7fcc.json` (today's run) decodes to `--sources github hackernews huggingface reddit x`, deliberately omitting arxiv. Same pattern on 04-17, 04-19, 04-20, 04-21 (4 of last 5 days, 0 arxiv items each). Standalone `arxiv.collect()` works fine — 120 papers in 103s. The omission was the foreman daily-report sub-agent reading SKILL.md L200 (`--sources reddit hackernews github` example), getting the imitation cue, and enumerating sources without arxiv.
- **Replaced `--sources` allow-list with `--skip` deny-list in `skills/tracking-list/scripts/collect.py`**: Default behavior now runs all 6 collectors. To opt out, callers must explicitly name what they're dropping (`--skip arxiv reddit`). Allow-list semantics let agents silently omit collectors by forgetting to list them — deny-list forces the omission to be visible. Cache key now uses sorted `--skip` value instead of `--sources` (so the cache key changes — old caches will be re-built once on next run, no migration needed). Validation added: unknown source names in `--skip` raise `ValueError` with the valid list, and `--skip` covering every collector is rejected.
- **SKILL.md updated**: Step 1 example now shows `--skip` semantics; "5 collectors" → "6 collectors" (X/Twitter is now an in-process collector via `lib/x_agent.py`, not a separate web-search step). Disambiguated from the Step 3 `--exclude` content-type filter.

## [1.4.0] - 2026-04-21

### New Features
- **KOL Voices section in `gen-email`**: Daily digest emails now render an independent "KOL Voices" block after the main items, mirroring the `## KOL Voices` block in `report_{date}.md` and the dedicated KOL channel in `gen-social`. Without it, KOL takes either get suppressed by the 7+ verification gate (KOL voices score 4-7 by design — they're commentary, not vendor announcements that need cross-source verification) or get mixed into the main feed where they read as off-topic. Three new env vars: `EMAIL_KOL_ENABLED` (default `true`), `EMAIL_KOL_MIN_SCORE` (default `4`, deliberately lower than `EMAIL_MIN_SCORE`), and `EMAIL_KOL_MAX_ITEMS` (default `5`). On quiet KOL days the section still renders with a "today's KOL voices were quiet" line so subscribers see the section is alive — set `EMAIL_KOL_SHOW_EMPTY=false` to omit it entirely on quiet days, or `EMAIL_KOL_ENABLED=false` to suppress permanently. The send manifest now reports `kol_items_count` and `kol_section_shown` for visibility.

## [1.3.0] - 2026-04-20

### New Features
- **Email subscription (`gen-email`)**: New skill that delivers the daily digest as multipart HTML email via SMTP — the first true automated push channel in the pipeline. Set `EMAIL_ENABLED=true` plus SMTP credentials (`EMAIL_SMTP_HOST/PORT/USER/PASSWORD`) and a recipient list (`EMAIL_RECIPIENTS` env or `EMAIL_RECIPIENTS_FILE` JSON). Per-recipient overrides for language and minimum score, automatic plain-text fallback, optional attachment of `message_{date}.png`, and `EMAIL_DRY_RUN` for local-only preview rendering. Adds RFC 8058 `List-Unsubscribe` headers when `EMAIL_LIST_UNSUBSCRIBE` is set so mainstream clients show one-click unsubscribe.
- **Recipient management**: `lib/recipients.py` loads recipients from env list or JSON file. JSON entries support `lang`, `min_score`, and `active` fields for per-recipient customization without touching env vars.
- **Send manifest**: Each run writes `email_{date}_manifest.json` with per-recipient status (`sent` / `failed`) and error text — enables retry logic and visible failure tracking without log scraping.

### Documentation
- New `docs/email-setup.md` with SMTP quick-start for Gmail (App Password), QQ Mail, Outlook, and Alibaba Cloud Enterprise Mail.
- `skills/gen-email/SKILL.md` documents all 17 `EMAIL_*` env vars and the recipients JSON schema.

### Bug Fixes
- **IPv6 fallback in SMTP connect**: `lib/email_sender.py` now retries IPv4-only when the first connect attempt fails with `ENETUNREACH` (errno 101). Some hosts — common in containers, cloud VMs, and offices with broken IPv6 egress — get an AAAA record from DNS but cannot route it, causing `smtplib` to fail before reaching auth. The retry preserves the original hostname so TLS SNI / cert validation still match `smtp.gmail.com`.
- **IPv6 fallback for collectors**: The same IPv6 → IPv4 retry now applies to `lib/http.py` (used by arxiv / Hacker News / GitHub / HuggingFace) and `lib/reddit.py`. Extracted into `lib/net.py` as `force_ipv4_only()` / `is_ipv6_unreachable()` helpers and reused from `lib/email_sender.py`. On hosts with broken IPv6 routing the collectors used to silently return zero items; they now switch to IPv4 after one failed attempt and continue normally.
- **Reddit collector now logs network errors**: `lib/reddit.py:_fetch_json` previously swallowed every `URLError` / `OSError` / `JSONDecodeError` and returned `None`, so the operator saw "24 entities checked, 0 items, 0 errors" with no clue why. It now logs the failing URL and exception class via `_log()` (visible when running in a TTY, matching the rest of the collectors).
- **arXiv 3-day default window**: arXiv papers don't drop daily in every category — most days the cs.AI feed has nothing newer than 2-3 days back. `lib/arxiv.py` now widens the caller's 1-day window to 3 days by default. Override via `ARXIV_LOOKBACK_DAYS=N` (set to `1` to restore strict 24h behavior).
- **Cache key includes `--sources`**: `skills/tracking-list/scripts/collect.py` previously hashed only `(date, depth)`, so a partial-source run (e.g. `--sources reddit github`) would write a 2-source report into the cache that a subsequent full run would happily read back as complete. The cache key now includes the sorted sources list.

## [1.2.9] - 2026-04-16

### Improvements
- **Social media template cleanup**: Ship only one default template per platform — X `briefing` and Xiaohongshu `news-briefing`. All other persona templates are local-only examples
- **Xiaohongshu news-briefing template**: Add priority indicators (🔴🟠🟡 by importance score), "今日数字" data highlights section, and ultra-compact telegraph format
- **SKILL.md simplification**: Streamline style tables to show only shipped templates, with guidance to copy-and-customize for custom personas

## [1.2.8] - 2026-04-15

### Improvements
- **HuggingFace model metadata enrichment**: Fetch technical specs (parameter count, architecture, license, base model) from HuggingFace model API alongside README descriptions. Summaries now include structured specs like "31B params, Gemma3 architecture, apache-2.0"
- **Mandatory source links in MESSAGE digest**: Every digest item must now have a source link — items without `source_url` trigger URL construction from known patterns (HuggingFace model page, GitHub repo, arXiv abstract). Items with no findable URL are dropped entirely. Zero-link items are treated as critical formatting errors

## [1.2.7] - 2026-04-15

### Improvements
- **GitHub release scoring fix**: Release items no longer inherit the repo's lifetime star count as engagement — a patch bump on a 100K-star repo no longer outscores major industry news. Trending repos (OSS Insight) still use star-delta scoring since the surge IS the story
- **MESSAGE category balance**: Add `MESSAGE_CATEGORY_BALANCE` (default `true`) with per-type slot caps (product max 4, model max 3, benchmark max 2, financing max 2) to ensure content diversity in message digests instead of pure top-N by score

## [1.2.6] - 2026-04-14

### New Features
- **`--intro` parameter**: Display product introduction page and stop — no data collection, useful for first-time users

### Improvements
- **Rebranded to MorningAI**: All report headers, templates, and references updated from "AI News Daily" to "MorningAI"
- **HuggingFace model descriptions**: Fetch README.md from repo instead of API cardData for richer, more accurate model descriptions
- **Reddit concurrent requests**: Parallel subreddit fetching for faster collection; collector timeout increased to 600s
- **Infographic generation**: Cover image always generated; combined long image preserved as default output
- **GitHub trending discovery via OSS Insight**: Integrated OSS Insight API (`/v1/trends/repos/`) to discover trending repos by 24h activity (stars, forks, PRs, pushes). Matched repos cross-verify with entity releases; unmatched repos surface as "GitHub Trending" discovery items. Replaces unused `search_trending()` dead code
- **Example dates updated**: All sample data and references updated from 2026-04-08 to 2026-04-14

### Fixes
- **content_type auto-classification**: All collectors previously left `content_type` empty — added heuristic classifier (`lib/classify.py`) using source type + keyword patterns to assign product/model/benchmark/financing. Integrated into pipeline before scoring
- **HuggingFace summary enrichment**: Summary was just metadata stats (pipeline/downloads/likes). Now fetches model card description via `/api/models/{id}` concurrently, with metadata fallback
- **HackerNews summary enrichment**: Summary was "HN discussion (N pts, N comments)". Now uses story_text for text posts, domain+engagement for link posts, structured discussion points from top comments
- **Cross-source linking fixed**: Title-based Jaccard matching produced ~0 similarity across sources due to format differences (HF model IDs vs HN natural language vs GH repo+version). Added source-aware title normalization, entity match bonus (+0.25), URL domain matching (+0.15), and lower threshold (0.25) for same-entity pairs
- **Scoring distribution spread**: 90% of items clustered at 5-7 due to compressed engagement normalization and blanket verification penalty. Reduced engagement divisors (HN/Reddit 8→6, GitHub 10→7, HF 12→8), added percentile rescaling to 2.0-9.5 range, removed the -0.5 penalty for unverified 7+ items
- **HackerNews noise filtering**: Added noise pattern filters (outage complaints, career Ask HNs, rants) and raised minimum points threshold from 2 to 5, with high-engagement bypass (100+ pts exempt)

## [1.2.5] - 2026-04-14

### Improvements
- **Claude Code skill discovery via symlink**: Add `skills/morning-ai/SKILL.md` symlink pointing to root `SKILL.md`, enabling Claude Code to discover the main skill through its `skills/` directory scan while keeping root `SKILL.md` intact for Codex, OpenCode, and OpenClaw

## [1.2.4] - 2026-04-14

### Fixes
- **Reddit community links fixed**: Replace dead/private subreddit links — r/Qwen → r/Qwen_AI (original was private), r/HailuoAI → r/HailuoAiOfficial (original didn't exist), removed r/TencentAI (doesn't exist)
- **Message digest: prioritize substance over vanity metrics**: Summary now requires answering "what is it" + "why it matters" instead of leading with download/star counts. GitHub Trending items lead with project description, star count as supporting context

## [1.2.3] - 2026-04-14

### Improvements
- **Reddit: entity-specific subreddit support**: Each entity can now define dedicated subreddits via `Reddit Community` field (e.g. `r/DeepSeek`, `r/ClaudeAI`). The collector fetches hot posts directly from these communities — no keyword search needed since the entire subreddit is about that entity
- **Two-phase Reddit collection**: Phase 1 fetches hot posts from entity-specific subreddits; Phase 2 keyword-searches general subreddits (`MachineLearning`, `LocalLLaMA`, `artificial`, `singularity`) as before, with cross-phase deduplication
- **25 entity-specific subreddits added**: Covers AI labs (r/OpenAI, r/ChatGPT, r/ClaudeAI, r/Gemini, r/DeepSeek, r/Grok, etc.), coding agents (r/cursor, r/Windsurf, r/ClineAI), model infra (r/MistralAI, r/perplexity_ai), vision/media (r/midjourney, r/StableDiffusion, r/SunoAI), and apps (r/CharacterAI)
- **Custom entity template updated**: `Reddit Community` added as a supported platform field in `custom-example.md`
- **Cache TTL default reduced to 1 hour**: `--cache-ttl` now defaults to 1h; added `--no-cache` and `--clear-cache` flags
- **Cover image switched to 9:16 portrait**: Cover infographic now uses 9:16 portrait (same as per-type sections) for seamless vertical stitching into combined long image

## [1.2.2] - 2026-04-14

### Improvements
- **Message digest: all items require traceable source**: Every item must have a valid `source_url` to an authoritative primary source, regardless of score. 7+ score items additionally require cross-source verification (`verified == true`, 2+ independent sources)
- **Message digest: inline source links by default**: Each item ends with a `🔗 URL` source link. Changed `MESSAGE_LINKS` default from `bottom` to `inline`
- **Examples switched to English**: All examples in gen-message SKILL.md and digest template are now in English for consistency
- **Enhanced X/Twitter search**: Multi-layer search strategy (official accounts → CEO/personnel → KOLs), RT/quote tweet tracing to original post time, structured per-category search with source priority hierarchy

## [1.2.0] - 2026-04-14

### New Features
- **Message digest mode** (`MESSAGE_ENABLED=true`): Generate concise, copy-paste-friendly message digests for sharing on messaging platforms (WeChat, Telegram, Slack). Each item gets a bold title + one-line summary + emoji marker (🔥/⭐/🔷 by score). Optional 9:16 portrait image for visual sharing. Configurable via `MESSAGE_MIN_SCORE`, `MESSAGE_MAX_ITEMS`, `MESSAGE_LINKS` (bottom/inline)

## [1.1.8] - 2026-04-14

### Fixes
- **Fix plugin manifest validation**: Remove `skills` and `hooks` fields from `plugin.json` (Claude Code auto-discovers root `SKILL.md`); remove `$schema` and move `description` into `metadata` in `marketplace.json` to match current Claude Code schema

## [1.1.7] - 2026-04-14

### Fixes
- **Fix skills field format**: Revert to `["./"]` (array) for `.claude-plugin/plugin.json` — matches working plugins (e.g. last30days). Previous changes to `"SKILL.md"` caused "skills: Invalid input" validation error
- **Remove redundant `.agents/plugins/`**: Deleted `marketplace.json` that used `../../` path escaping; OpenCode/Hermes discover skills via `AGENTS.md` at repo root

## [1.1.4] - 2026-04-13

### New Features
- **OpenCode & Hermes Agent support**: Added installation guides for OpenCode (native + compatible paths) and Hermes Agent (`hermes skills install`); updated sync.sh deploy targets

### Improvements
- **Factual detail verification rules**: All specific numbers (parameter counts, benchmark scores, pricing, context lengths, etc.) must now be verified from authoritative primary sources before inclusion — omit rather than guess
- **Date display restricted to cover image**: Per-type section infographic images (Model/Product/Benchmark/Funding) no longer show the date in the header; only the cover image displays the date

## [1.1.3] - 2026-04-13

### Breaking Changes
- **Removed YouTube, Discord, and ScrapeCreators data sources**: Streamlined to 5 automated sources (Reddit, HN, GitHub, HuggingFace, arXiv) + agent-driven X/Twitter search
- **X/Twitter switched to agent web search**: No API key needed — X updates are now discovered via agent web search instead of dedicated collectors

### Improvements
- **Default to long image mode**: Infographics now generate as stitched long images by default
- **Cover image switched to 16:9 landscape**: Cover infographic now uses 16:9 aspect ratio; per-type sections remain 9:16 portrait
- **Removed sparse image strategy**: Always generate cover + per-type sections + stitch into long image, regardless of item count
- **English as default report language**: Reports are now written in English by default unless `--lang` is specified
- **Cleaned up manifest examples**: Removed redundant `aspect_ratio` field from image generation manifests
- **Simplified tool compatibility docs**: Removed references to Amp and Jules; updated GitHub token prefix example

## [1.1.2] - 2026-04-13

### Improvements
- **Richer report detail for high-score items (7+)**: Added required "Why It Matters" analysis section and optional "Key Data" metrics table to record format
- **Enhanced mid-score items (5-6)**: Upgraded from one-line summaries to two-line format with concrete details, numbers, and source links
- **More informative TLDR**: Each TLDR entry now includes an Impact line explaining industry significance
- **Detail quality rule**: Summary bullet points now explicitly require specific numbers (versions, benchmarks, pricing, parameters) instead of vague descriptions

## [1.1.1] - 2026-04-10

### New Features
- **Style presets for infographics**: 5 built-in visual styles (classic, dark, glassmorphism, newspaper, tech) selectable via `IMAGE_STYLE` config
- **Style-aware image stitching**: Background color matches selected style when stitching multi-section infographics
- **Content density enforcement**: Automatic injection of content rendering rules to maximize information display in generated images
- **Section continuity rules**: Seamless visual flow between stitched image sections with per-style overrides

## [1.1.0] - 2026-04-10

### New Features
- **Onboarding flow**: First-time interactive setup guide with Step 0 gate to prevent agents skipping configuration
- **Custom entity watchlists**: Users can add personal entities to track beyond the built-in registries
- **Language control**: Default English output with `--lang` override for other languages
- **Source links**: All report items now include source URLs for reader click-through
- **Adaptive infographic generation**: Long-image layout with per-image aspect ratio support
- **MiniMax region support**: Separate `intl` and `cn` API endpoints for image generation
- **SQLite leaderboard snapshots**: Track benchmark ranking changes over time
- **Multi-image infographic**: Pluggable multi-image stitching for cover generation
- **Cron/scheduled execution**: Scheduling metadata and documentation for unattended daily runs

### Multi-Platform Support
- **Codex plugin**: Added `.codex-plugin/` with interface metadata for OpenAI Codex CLI
- **AGENTS.md**: Cross-agent skill discovery for Codex and other agent platforms
- **Gemini CLI extension**: `gemini-extension.json` with environment variable settings

### Improvements
- Refactored from Claude Code-only plugin to universal skill format
- Renamed project identity from `ai-tracker` to `morning-ai`
- Restructured `agents/` directory to `entities/` for clarity
- Colocated scripts with their skill definitions; promoted `lib/` to top level
- Output generated files to caller's working directory instead of skill directory
- Expanded tracked entities from 76+ to 80+
- Extracted KOL entities from benchmarks-academic into standalone registry
- Added new leaderboards: Vending-Bench, SimpleBench, Repo Bench
- Added KTransformers and Hermes Agent to coding-agent registry
- Merged `frontier-labs` and `china-ai` into unified `ai-labs` entity file

### Fixes
- Fixed `sys.path` resolution: use `parents[3]` to reach project root from nested scripts
- Fixed Claude Code install command: use `marketplace add` without `/plugin` prefix

## [1.0.0] - 2026-04-07

Initial release.

- 9 data sources: X/Twitter, Reddit, Hacker News, GitHub, HuggingFace, arXiv, YouTube, Discord, web search
- 76+ tracked AI entities across labs, models, benchmarks, apps, and KOLs
- Scoring and deduplication engine
- Markdown report generation with configurable templates
- Claude Code plugin with marketplace listing
