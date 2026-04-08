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

Dispatch 8 Sub Agents concurrently:

| # | Agent | Status | Draft Path | Discoveries | 7+ Scores |
|---|-------|------|-----------|--------|------|
| 1 | frontier-labs | ⏳ | | | |
| 2 | model-infra | ⏳ | | | |
| 3 | china-ai | ⏳ | | | |
| 4 | coding-tools | ⏳ | | | |
| 5 | ai-apps | ⏳ | | | |
| 6 | vision-media | ⏳ | | | |
| 7 | benchmarks-academic | ⏳ | | | |
| 8 | trending-discovery | ⏳ | | | |

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

## Phase 5: Generate Cover Infographic

- [ ] Call `/gen-infographic` skill to get specification
- [ ] Select top 4-5 updates to build Prompt
- [ ] Call gen_images to generate 16:9 PNG
- [ ] Verify image content
- [ ] Insert at report beginning

---

## Phase 6: Final Review

- [ ] All phase checkboxes checked
- [ ] report_{date}.md complete
- [ ] news_infographic_{date}.png correct
- [ ] Mark as "Status: Completed"

**Status**: ⏳ In Progress

---

## Final Deliverables

- 📄 `report_{DATE}.md` - Daily Report Markdown
- 🖼️ `news_infographic_{DATE}.png` - Cover Infographic
