# Infographic Styles

MorningAI generates social-ready infographics in 5 visual styles. Set `IMAGE_STYLE` in your `.env` to choose.

## classic (default)

Clean editorial magazine aesthetic.

- **Background**: Off-white (#FAFAF8)
- **Typography**: Inter / DM Sans — modern sans-serif
- **Accents**: Navy (#1B2A4A), coral (#E8634A), teal (#2A9D8F)
- **Layout**: Card-based with subtle shadows, generous whitespace
- **Best for**: Professional reports, team sharing, documentation

```
┌─────────────────────────────────────────────┐
│  MorningAI · 2026-04-08                 │
│─────────────────────────────────────────────│
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ ★ 9.2  Anthropic                    │    │
│  │ Claude 4.5 Sonnet released          │    │
│  │ +18% SWE-Bench, 200K context        │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ ★ 8.8  Google DeepMind              │    │
│  │ Gemini 2.5 Flash public preview     │    │
│  │ 1M context, native multimodal       │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ ★ 8.5  Cursor                       │    │
│  │ Background Agents GA                │    │
│  │ Autonomous multi-file refactoring   │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  8 verified updates · 6 sources · 80+ entities │
└─────────────────────────────────────────────┘
```

## dark

Dark mode with electric accents — ideal for developer audiences.

- **Background**: Charcoal (#0D1117) to dark grey (#161B22)
- **Typography**: Inter — clean and readable on dark
- **Accents**: Electric blue (#58A6FF), violet (#BC8CFF), emerald (#3FB950)
- **Layout**: Cards with subtle borders, glow effects on high-score items
- **Best for**: Developer communities, X/Twitter posts, Discord sharing

```
┌─────────────────────────────────────────────┐
│  ░░ MorningAI · 2026-04-08 ░░           │
│─────────────────────────────────────────────│
│                                             │
│  ┌─ ◆ 9.2 ─────────────────────────────┐   │
│  │  Anthropic · Claude 4.5 Sonnet      │   │
│  │  +18% SWE-Bench · 200K ctx · 40% ↑  │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌─ ◆ 8.8 ─────────────────────────────┐   │
│  │  Google · Gemini 2.5 Flash          │   │
│  │  1M context · multimodal · free tier │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌─ ◆ 8.5 ─────────────────────────────┐   │
│  │  Cursor · Background Agents GA      │   │
│  │  Cloud sandbox · 10 concurrent      │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ▓ 8 verified · 6 sources · 47.3s          │
└─────────────────────────────────────────────┘
```

## glassmorphism

Frosted glass cards on soft gradient — modern SaaS aesthetic.

- **Background**: Soft gradient (lavender → peach → sky blue)
- **Typography**: Plus Jakarta Sans — rounded and friendly
- **Accents**: White glass cards with blur backdrop, pastel highlights
- **Layout**: Overlapping translucent cards with rounded corners
- **Best for**: Product Hunt posts, LinkedIn sharing, design-forward audiences

```
┌─────────────────────────────────────────────┐
│  ·····  MorningAI  ·····  2026-04-08    │
│  ░░░░░░░░░░░░ gradient bg ░░░░░░░░░░░░░░░  │
│                                             │
│    ╭╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╮    │
│    ┊  ★ 9.2  Anthropic                ┊    │
│    ┊  Claude 4.5 Sonnet released      ┊    │
│    ╰╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╯    │
│      ╭╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╮    │
│      ┊  ★ 8.8  Google DeepMind       ┊    │
│      ┊  Gemini 2.5 Flash preview     ┊    │
│      ╰╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╯    │
│        ╭╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╮    │
│        ┊  ★ 8.5  Cursor              ┊    │
│        ┊  Background Agents GA       ┊    │
│        ╰╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╯    │
│                                             │
└─────────────────────────────────────────────┘
```

## newspaper

Classic newsprint with serif typography — traditional editorial gravitas.

- **Background**: Cream (#FFF8F0)
- **Typography**: Playfair Display (headlines) + Source Serif Pro (body)
- **Accents**: Black (#1A1A1A), crimson (#8B0000), gold (#B8860B) for scores
- **Layout**: Multi-column broadsheet, horizontal rules, dateline headers
- **Best for**: Newsletter embeds, email digests, executive briefings

```
┌─────────────────────────────────────────────┐
│  THE AI DAILY          Tuesday, April 8 2026│
│═════════════════════════════════════════════│
│                                             │
│  CLAUDE 4.5 SONNET     │ CURSOR AGENTS GA   │
│  RELEASED              │ NOW AVAILABLE       │
│  ─────────────────     │ ──────────────────  │
│  Anthropic unveils     │ Background agents   │
│  mid-tier model with   │ reach general       │
│  18% coding gains,     │ availability with   │
│  200K context.  [9.2]  │ cloud sandbox. [8.5]│
│                        │                     │
│  GEMINI 2.5 FLASH      │ WINDSURF $200M      │
│  PUBLIC PREVIEW        │ SERIES C            │
│  ─────────────────     │ ──────────────────  │
│  1M context, free      │ AI IDE valued at    │
│  tier on AI Studio,    │ $3B. Largest round  │
│  multimodal.    [8.8]  │ in coding tools.[7.1]│
│                                             │
│  ── 26 updates · 8 verified · 80+ entities ─│
└─────────────────────────────────────────────┘
```

## tech

Terminal aesthetic with monospace — for the hacker crowd.

- **Background**: Near-black (#0A0A0A)
- **Typography**: JetBrains Mono / Fira Code — monospace throughout
- **Accents**: Cyan (#00D4FF), green (#00FF41), amber (#FFB000)
- **Layout**: CLI-style with `>` prompts, box-drawing characters, scan-line effects
- **Best for**: Developer forums, GitHub README embeds, terminal screenshot aesthetic

```
┌─────────────────────────────────────────────┐
│  > morning-ai --date 2026-04-08             │
│  > scanning 6 sources... done (47.3s)       │
│  > 186 raw → 26 deduped → 8 verified        │
│                                             │
│  [9.2] anthropic/claude-4.5-sonnet          │
│        +18% swe-bench | 200k ctx | api live │
│                                             │
│  [8.8] google/gemini-2.5-flash              │
│        1M ctx | multimodal | free tier      │
│                                             │
│  [8.5] cursor/background-agents             │
│        GA | cloud sandbox | 10 concurrent   │
│                                             │
│  [8.3] deepseek/v3-0407                     │
│        671B MoE | MIT license | HF weights  │
│                                             │
│  [8.0] openai/codex-cli                     │
│        open-source | MIT | full-auto mode   │
│                                             │
│  > 8 verified across 3+ sources             │
│  > next run: 2026-04-09 08:00 UTC+8         │
└─────────────────────────────────────────────┘
```

## Configuration

Set your preferred style in `.env`:

```env
IMAGE_STYLE=dark
IMAGE_GEN_PROVIDER=gemini
```

Or pass it inline:

```bash
/morning-ai --style glassmorphism
```

## Long Image Mode

All styles support vertical long-image stitching for mobile-friendly scrolling (e.g., WeChat Moments, Instagram Stories):

```env
IMAGE_STITCH=true
IMAGE_STITCH_ORIENTATION=vertical
```

This generates per-type images (model, product, benchmark, funding) and stitches them into a single 9:16 portrait image.
