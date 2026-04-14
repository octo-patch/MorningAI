# Changelog

## [1.2.1] - 2026-04-14

### Improvements
- **Message digest: inline source links by default**: Each item now ends with a `🔗 URL` source link. Changed `MESSAGE_LINKS` default from `bottom` to `inline` so readers can immediately access the original source for every item

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
