# Changelog

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
