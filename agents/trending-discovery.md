# Trending Discovery Agent

Entity registry for trending platform scanning — discovers emerging AI tools, projects, and important updates beyond known entities.

---

## Scan Sources

### 1. GitHub Trending (AI/ML)

| Attribute | Info |
|------|------|
| **Trending Page** | https://github.com/trending?since=daily |
| **Focus Area** | AI/ML related trending repos |
| **Filter Criteria** | AI/ML related, significant star growth today |

### 2. Product Hunt

| Attribute | Info |
|------|------|
| **Daily Page** | https://www.producthunt.com |
| **Focus Area** | Newly launched products in AI category |
| **Filter Criteria** | AI/ML tags, top voted |

### 3. Hacker News Front Page

| Attribute | Info |
|------|------|
| **API** | https://hacker-news.firebaseio.com/v0/topstories |
| **Algolia Search** | https://hn.algolia.com/api/v1/search |
| **Focus Area** | AI/ML/LLM related top stories |
| **Filter Criteria** | Title or content contains AI/ML/LLM keywords, score > 50 |

### 4. Reddit Frontier Discussions

| Attribute | Info |
|------|------|
| **r/singularity** | https://reddit.com/r/singularity | AI frontier discussion |
| **r/artificial** | https://reddit.com/r/artificial | AI general discussion |
| **Filter Criteria** | Top upvoted posts within 24h |

---

## Working Rules

1. **Exclude known entities**: If discovered content belongs to another Agent's entity (e.g., OpenAI, Cursor, etc.), record but mark as "already covered by XX Agent"
2. **Focus on discovery**: Prioritize reporting the following types of discoveries:
   - Brand new AI tools/products debut
   - Open-source projects exploding (star count surge)
   - Important industry events (policy, partnerships, milestones)
   - Influential community discussions or controversies
3. **Scoring criteria**: Follow shared specification, but new tools/projects typically score 3-5, unless widespread attention

---

## Workflow

### Input Parameters

- `date`, `time_window_start`, `time_window_end`, `output_dir`

### Execution Steps

#### Step 0: Reference Specification
Refer to `skills/tracking-list/SKILL.md` for tracking scope, scoring criteria, and timeliness check rules.

#### Step 1: Initialize Draft
Copy `templates/draft_collector.md` to `{output_dir}/draft_trending-discovery_{date}.md`

#### Step 2: Check each source

```
FOR each source in [GitHub Trending, Product Hunt, HN, Reddit]:
    1. Fetch today's trending content
    2. Filter AI/ML related entries
    3. Exclude entities already covered by other Agents
    4. Timeliness check (within 24h)
    5. Valid discovery -> append to Draft
    6. Check Checkbox + save Draft
END FOR
```

#### Step 3: Final Review
Confirm completion rate = 100%.

### Output Format

```json
{
  "status": "completed",
  "draft_path": "{output_dir}/draft_trending-discovery_{date}.md",
  "completion": {
    "total_sources": 4,
    "checked_sources": 4,
    "completion_rate": "100%"
  },
  "results": {
    "product": 0, "model": 0, "benchmark": 0, "funding": 0,
    "skipped": 0, "high_value_count": 0
  }
}
```
