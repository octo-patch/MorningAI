# AI News Tracking - Main Work Plan

**Date**: {DATE}
**Time Window**: [{YESTERDAY} 08:00, {TODAY} 08:00) UTC+8
**Tracking Types**: {ACTIVE_TYPES}
**Generated At**: {TIMESTAMP}

---

## Phase 1: Initialization

- [ ] Determine date and time window
- [ ] Determine tracking types (default all)
- [ ] Create drafts/ directory
- [ ] Copy template files

---

## Phase 2: Concurrent Collection Tasks

Dispatch 7 Sub Agents concurrently:

| # | Agent | Status | Draft Path | Discoveries | 7+ Scores |
|---|-------|------|-----------|--------|------|
| 1 | ai-labs | ⏳ | | | |
| 2 | model-infra | ⏳ | | | |
| 3 | coding-tools | ⏳ | | | |
| 4 | ai-apps | ⏳ | | | |
| 5 | vision-media | ⏳ | | | |
| 6 | benchmarks-academic | ⏳ | | | |
| 7 | trending-discovery | ⏳ | | | |

---

## Phase 3: Collection Completion Verification

- [ ] All Agents returned results
- [ ] Each Agent completion rate = 100%
- [ ] No unchecked source items

---

## Phase 4: Aggregate and Generate Report

- [ ] Call `/tracking-list` skill to get specification
- [ ] Copy draft_main template
- [ ] Extract valid records from each Draft
- [ ] Filter by type (exclude exclude_types)
- [ ] Deduplicate by source_url
- [ ] Sort by score
- [ ] Generate report_{date}.md

### Summary Stats

| Type | Count | 7+ Scores |
|------|------|------|
| Model | | |
| Product | | |
| Benchmark | | |
| Funding | | |
| **Total** | | |
| Skipped | | |

---

## Phase 5: Generate Infographics (Optional)

- [ ] Call `/gen-infographic` skill to get specification
- [ ] Build cover prompt (top 4-5 across all types)
- [ ] Build per-type prompts (for types with 7+ items)
- [ ] Generate all images (via native tool OR `python3 scripts/gen_infographic.py --batch`)
- [ ] Verify image content (if generated)
- [ ] Insert cover at report beginning, per-type at section tops (if generated)

> Skip this phase if `IMAGE_GEN_PROVIDER=none` or no image generation capability is available.

---

## Phase 6: Final Review

- [ ] All phase checkboxes checked
- [ ] report_{date}.md complete
- [ ] news_infographic_{date}.png correct (if generated)
- [ ] Mark as "Status: Completed"

**Status**: ⏳ In Progress

---

## Final Deliverables

- 📄 `report_{DATE}.md` - Daily Report Markdown
- 🖼️ `news_infographic_{DATE}.png` - Cover Infographic (if image generation is configured)
- 🖼️ `news_infographic_{DATE}_{type}.png` - Per-type Infographics (if configured)
