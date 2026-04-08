---
name: tracking-list
description: Unified AI News Tracking Specification - covers Product/Model/Benchmark/Funding types with tracking scope, source standards, timeliness checks, scoring criteria, and record format
---

# AI News Tracking - Unified Specification

This document defines the shared specification for scoring, formatting, and validating AI news items.

---

## Tracking Type Definitions

This tracking system categorizes AI industry updates into **4 types**. Each record must be labeled with its type. The main Agent can exclude unwanted types via `exclude_types` (All tracked by default).

### Type 1: Product

Feature/version updates for AI tools and platforms.

| Include | Exclude |
|---------|---------|
| New feature launch (officially released) | Tips sharing (key people sharing usage tips, not new features) |
| Official version release (e.g. v2.0.0) | Pure marketing content (promotions, retweet giveaways) |
| Major capability upgrade (new model integration, new workflow) | Minor UI tweaks (interface changes not affecting functionality) |
| API/SDK update (new endpoints, new parameters) | Minor mobile update (bug fixes only) |
| Open-source project release (GitHub Releases) | |
| Product pricing change | |

**Source Priority**: Changelog/Release Notes > GitHub Releases > Official Blog > Official X > Key People X

**Key People Post Handling**:
- Feature/version release → must cross-verify with Changelog
- Tips sharing ("I recently discovered...", "pro tip") → not included
- Announcement outside window but feature landed within window → use feature landing as primary, announcement as background

### Type 2: Model

AI model releases, updates, and open-sourcing (including LLM, vision models, multimodal models).

| Include | Exclude |
|---------|---------|
| New model release (flagship model official launch) | App feature update (ChatGPT/Gemini interface features) |
| Model version update (series iteration versions) | Enterprise/Team product update |
| Model capability upgrade (context, multimodal) | Subscription change |
| Model API update (new endpoints, pricing adjustments) | Marketing campaigns, user milestones |
| Open-source model weights release (GitHub, HuggingFace) | |
| Multimodal model release (image, video, voice) | |
| Image/video generation model release | |

**Source Priority**: Official Blog > Official X > API Changelog > GitHub/HuggingFace > Key People X > arXiv

### Type 3: Benchmark

Benchmark leaderboard changes, benchmark results, academic papers, technical reports.

| Include | Exclude |
|---------|---------|
| Official benchmark results | Survey papers (lacking novelty) |
| Authoritative leaderboard ranking changes (LMSYS, Artificial Analysis, VLM Arena) | Non-reproducible research |
| High-value academic papers (arXiv, top conferences) | Duplicate coverage (secondhand news restatements) |
| Major vendor technical reports/Research Blog | |
| Open-source research (papers with code/weights) | |
| Architecture innovation, training method breakthroughs | |
| Interpretability/alignment/safety research | |

**Source Priority**: Benchmark institutions > arXiv > Official Research > HuggingFace Papers > KOL > Papers with Code > Reddit

### Type 4: Funding

Major funding, acquisitions/mergers, strategic partnerships, milestone events.

| Include | Exclude |
|---------|---------|
| Large funding (Series B+ **or** amount >= $100M) | Small seed/angel round (< $50M and Series A or below) |
| Acquisition/merger (AI-related companies) | Pure rumors/unconfirmed ("reportedly", "sources say") |
| Major strategic partnership (official integration with mainstream platforms) | Not directly AI-related acquisitions/funding |
| Strategic investment (involving AI companies) | Regular milestone (users < 1M) |
| Major milestone (users >= 1M / ARR >= $100M / DAU >= 1M) | Unilateral announcement, no response from counterparty |

**Source Priority**: Bilateral official confirmation > Crunchbase/PitchBook > Authoritative media (TechCrunch/The Verge)

**Verification Rules**:
| Event Type | Inclusion Criteria | Verification Method |
|------------|-------------------|---------------------|
| Acquisition/merger | AI-related companies | Bilateral official confirmation **or** authoritative media coverage |
| Large funding | Series B+ **or** >= $100M | Official announcement **or** Crunchbase/PitchBook confirmation |
| Major milestone | Users >= 1M **or** ARR >= $100M | Official announcement **or** third-party data platform verification |
| Major partnership | Official integration with mainstream platforms | Both parties confirmed **or** feature subsequently launched |

---

## Source Standards

### Source Priority (General)

| Priority | Source Type | Credibility | Handling |
|----------|------------|-------------|----------|
| 1 | Official Blog/News | Highest | Accept directly |
| 2 | Official Changelog/Release Notes | Highest | Accept directly |
| 3 | Official X/Twitter | High | Accept directly |
| 4 | GitHub Releases | High | Accept directly |
| 5 | Key People X | Fairly High | Requires cross-verification |
| 6 | HuggingFace | Medium-High | Accept directly |
| 7 | arXiv | Medium-High | Accept directly |
| 8 | Benchmark institutions | Medium | Accept directly (for benchmark information) |
| 9 | YouTube Official Channel | Medium | Accept directly |
| 10 | Discord Official Announcement | Medium | Accept directly |
| 11 | Opinion Leaders/KOL | Reference | Must trace to official channel for confirmation |
| 12 | Industry Media | Reference | For lead discovery only, must trace to source |

### Prohibited Actions

- Using news sites as primary source (for lead discovery only)
- Using search results as main information source
- Including secondary source information without tracing verification

### Cross-verification Rules

| Score | Verification Requirement |
|-------|------------------------|
| **7+** | Must have 2+ independent sources confirmed |
| **5-6** | Recommended 1+ other source corroboration |
| **Below 5** | Single credible source sufficient |

### Timeliness Double-check Rules

For the following scenarios, **a double-check is required** (confirm the original event date through additional searches or official timelines):

1. **No clear date annotation**: Page content does not show a specific publish date → search `"{product name} release date"` or `"{product name} announced"` to confirm
2. **Only third-party sources**: Event only reported on third-party media/platforms, no official primary source → trace to official announcement to confirm date
3. **Persistent state information**: Leaderboard rankings, product pricing, feature availability, etc. → confirm the date of the first state change, not the current state
4. **Vague time words like "recently"/"this month"**: Source uses "recently", "this month", etc. → cannot be accepted directly, must find precise date
5. **Date anomaly**: Event seems too major but wasn't covered by mainstream media within window → likely an old event, requires additional verification

**Events where date cannot be confirmed → downgrade to skip, annotate "date cannot be confirmed"**

---

## Timeliness Validation Rules

### Core Principle: Event date ≠ Page date

> **Key Rule: must confirm the "actual event date", not "page accessible date" or "page last updated date".**

A page being currently accessible does not mean the event it describes occurred within the window. Common misjudgment scenarios:

| Common Misjudgment Scenarios | Appearance | Correct Handling |
|------------------------------|------------|-----------------|
| Changelog page currently accessible | Page shows multiple historical entries | Check each entry's own date annotation |
| Leaderboard currently shows a model's ranking | Model currently on the list | Confirm the date the ranking change first occurred |
| Third-party platform page introduces a product | Page exists | Confirm the product's original release date, not the platform's listing date |
| News media reprints old news | Article publish date within window | Trace to original event date |
| Product website shows a feature | Feature currently available | Confirm the date the feature first launched/released |

**Determination Process**:
1. Find the event's **original announcement** (official blog, Release Notes, first X post)
2. Extract that announcement's **publish date** (not page last-modified)
3. Convert that date to UTC+8
4. Determine whether it falls within `[time_window_start, time_window_end)`
5. If the original date cannot be confirmed → **do not include**, record in skipped records and annotate "date cannot be confirmed"

### Time Window

- **Standard Window**: `[yesterday 08:00, today 08:00) UTC+8`
- **Window Length**: 24 hours

### Time Conversion

| Source | Timezone | Conversion |
|--------|----------|------------|
| X/Twitter API | UTC | +8 hours → UTC+8 |
| Official Blog (US) | PST/PDT | +16/+15 hours → UTC+8 |
| Official Blog (China) | UTC+8 | No conversion needed |
| GitHub Releases | UTC | +8 hours → UTC+8 |
| YouTube API | UTC | +8 hours → UTC+8 |
| Discord API | UTC | +8 hours → UTC+8 |
| Other sources | Case-by-case | Convert based on page annotation |

### Date Extraction Rules by Source Type

| Source Type | Correct Date Field | Incorrect Date Field | Notes |
|-------------|-------------------|---------------------|-------|
| **Changelog / Release Notes** | Entry's own date annotation (e.g. "April 7, 2026") | Page access date, page last-modified | A Changelog page contains multiple historical records; must check entry date |
| **Official Blog** | Article header publish date (usually in URL or byline) | "last updated" or page footer copyright year | Distinguish between "publish date" and "last edited date" |
| **GitHub Releases** | Release's `Published` date | Repository's `pushed_at` or commit date | A repository having daily commits does not mean a new Release |
| **X/Twitter** | Tweet's `created_at` timestamp | — | Use directly, but requires UTC → UTC+8 conversion |
| **Benchmark leaderboard** | Date of first recorded ranking change | Current leaderboard access date | Model "currently on list" ≠ "just entered list"; check changelog to confirm change date |
| **arXiv papers** | Submitted / Announced date | Page access date | Note v1 submission date vs subsequent version update dates |
| **News media** | Original event date cited in the report | Article publish date | Media may report days after the event occurred |
| **Product website** | Feature/model's first release announcement date | Current page existence date | Product pages exist permanently; does not mean newly released |
| **Third-party integration platform** (fal.ai, Freepik, etc.) | Original release date of the integrated product | Platform listing/posting date | Platform "day 0 integration" means platform went live that day, but the product itself may have been released earlier |

### Time Determination

```
Timeliness Check:
- ✅ Within window: Published Time ∈ [time_window_start, time_window_end)
- ❌ Outside window: Published Time < time_window_start or >= time_window_end
```

### RT/Quote Handling

- Retweets (RT) and Quotes must **trace to original post time**
- Use original publish time for determination of whether it falls within window
- Retweet time within window ≠ original fact within window

---

## Scoring Criteria

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Impact | 30% | Industry impact of the event |
| Differentiation | 25% | Whether industry-first/unique |
| Breakthrough | 20% | Degree of technical/strategic breakthrough |
| Coverage | 15% | Affected users/scope |
| Timeliness | 10% | Time-sensitivity value of the information |

### Score Levels

| Score | Level | Criteria |
|-------|-------|----------|
| **9-10** | Major Event | Industry landscape breakthrough. Flagship model release, revolutionary feature, game-changing acquisition/partnership, unicorn-level funding ($1B+), record-breaking milestone |
| **7-8** | Important Update | Noteworthy important progress. Model series new version, major feature upgrade, official partnership with mainstream platform, large funding ($100M-$1B), major milestone (1M users/$100M ARR) |
| **5-6** | Regular Update | Routine updates worth noting. Minor version update, routine features, medium funding ($50M-$100M), general academic improvement |
| **3-4** | Minor Update | API parameter adjustments, doc updates, bug fixes, UI adjustments |
| **1-2** | Trivial Update | Typo fixes, dependency upgrades, detail optimization |

### Scoring Reference by Type

#### Model Scoring Reference

| Score | Criteria |
|-------|----------|
| 9-10 | Major vendor next-gen flagship model, industry landscape breakthrough |
| 7-8 | Model series new version, major capability improvement, important open-source model |
| 5-6 | Minor version update, API pricing adjustment, context extension |
| 3-4 | API parameter adjustments, doc updates |
| 1-2 | Bug fixes, detail optimization |

#### Product Scoring Reference

| Score | Criteria |
|-------|----------|
| 9-10 | Brand new major version, revolutionary feature, industry first |
| 7-8 | New model integration, major feature upgrade, core capability improvement |
| 5-6 | Routine feature addition, experience optimization |
| 3-4 | Bug fixes, UI adjustments, minor updates |
| 1-2 | Typo fixes, dependency upgrades |

#### Benchmark/Paper Scoring Reference

| Score | Criteria |
|-------|----------|
| 9-10 | Paradigm-level breakthrough, potentially changing architecture design paradigm |
| 7-8 | High-value research, major technical innovation, with open-source code/weights |
| 5-6 | Valuable research, incremental improvement, validation experiments |
| 3-4 | Minor improvement, specific scenario optimization |
| 1-2 | Survey-type, lacking novelty, non-reproducible |

#### Funding Scoring Reference

| Score | Criteria |
|-------|----------|
| 9-10 | Major company acquires well-known AI company, unicorn-level funding ($1B+), competition-changing partnership |
| 7-8 | Large funding ($100M-$1B), strategic acquisition, major milestone (1M users/$100M ARR) |
| 5-6 | Medium funding ($50M-$100M), general partnership |

### Scoring Factors

| Factor | Positive Factors | Negative Factors |
|--------|-----------------|-----------------|
| Impact scope | Industry-wide attention, official ecosystem support | Specific scenarios only |
| Technical breakthrough | First-of-kind, breakthrough, architecture innovation | Follow-up, catching up, routine iteration |
| Availability | Immediately available | Preview, waitlist |
| Open-source level | Weights open-sourced, code open-sourced | API only, closed use only |
| Strategic value | Major acquisition/funding, competition-changing | Internal optimization only |

---

## Draft Record Format

### Valid Record Format

```markdown
### {Entity name} - {Event description}

| Field | Value |
|-------|-------|
| **Type Label** | Product / Model / Benchmark / Funding |
| **Timeliness Check** | ✅ Within window / ❌ Outside window |
| **Published Time** | YYYY-MM-DD HH:MM UTC+8 |
| **Event Type** | New feature / New model / Version update / Capability upgrade / Open-source release / Leaderboard change / Academic paper / Funding / Acquisition / Major partnership / Milestone / ... |
| **Partner/Acquirer** | (for Funding type) XX Company |
| **Amount/Scale** | (for Funding type) $XM / Series X / XM users |
| **Source** | [Source Name](URL) |
| **Score** | X.X |

**Summary**:
- Key point 1
- Key point 2
- Key point 3

**Multi-source Verification** (required for 7+):
- [Source 1](URL)
- [Source 2](URL)
```

### Academic Paper Record Format (Benchmark type)

```markdown
### {Entity name} - {Paper title}

| Field | Value |
|-------|-------|
| **Type Label** | Benchmark |
| **Timeliness Check** | ✅ Within window / ❌ Outside window |
| **Published Time** | YYYY-MM-DD HH:MM UTC+8 |
| **Event Type** | Academic paper / Technical report / Interpretability research |
| **arXiv** | [XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) |
| **GitHub** | [Org/Repo](URL) (if available) |
| **Source** | [Source Name](URL) |
| **Score** | X.X |

**Core Innovation**:
> One-sentence description of the paper's core innovation

**Research Significance**:
> Who is impacted? What has changed?

**Key Data**:
| Metric | Value |
|--------|-------|
| | |
```

### Skipped Record Format

```markdown
| Entity | Summary | Skip Reason | Source |
|--------|---------|-------------|--------|
| [Entity name] | [Content description] | Pure marketing / Unconfirmed rumor / Outside window / Duplicate coverage / Tips sharing | [link](url) |
```

---

## Workflow Specification

### Data Collection Workflow

```
FOR each source:
    1️⃣ Check source (X account, Changelog/Blog, GitHub Releases, YouTube, Discord, arXiv)
    2️⃣ Timeliness check (per time validation rules)
    3️⃣ Cross-verification (key people posts require cross-verification with official channels)
    4️⃣ Content classification → determine type label (Product/Model/Benchmark/Funding)
    5️⃣ Valid content → record with full format
    6️⃣ Irrelevant content → record in skipped items with reason
END FOR
```

### Type Classification Guide

When a piece of information may belong to multiple types, classify by the following priority:

| Scenario | Classification |
|----------|---------------|
| Product integrated new model | **Product** (core event is product feature change) |
| New model release brings product feature upgrade | **Model** (core event is model release) |
| Model leaderboard ranking change | **Benchmark** (core event is benchmark result) |
| Company received funding for model R&D | **Funding** (core event is funding) |
| Paper proposes new model architecture | **Benchmark** (academic papers fall under Benchmark) |

### Key Checkpoints

- [ ] All source Checkboxes checked
- [ ] All records contain complete format and correct type labels
- [ ] 7+ scores have multi-source verification
- [ ] Funding events have bilateral confirmation
- [ ] Completion rate = 100%

---

## Notes

1. **Type label required** - Each record must be labeled with type (Product/Model/Benchmark/Funding)
2. **Record as you check** - Append immediately upon discovery to the corresponding type section; don't backfill
3. **Strict timeliness** - Content outside window is not included
4. **Cross-verification** - 7+ must have multi-source confirmation
5. **Funding events need bilateral confirmation** - Unilateral announcement with no response from counterparty should be downgraded
6. **Complete records** - Including skipped content
7. **100% completion rate** - All Checkboxes must be checked
8. **Dynamic adaptation** - Entity list and scoring references should evolve with the industry
