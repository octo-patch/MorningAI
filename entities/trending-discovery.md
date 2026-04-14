# Trending Discovery Entity Registry

Entity registry for trending platform scanning — discovers emerging AI tools, projects, and important updates beyond known entities.

---

## Scan Sources

### 1. GitHub Trending (OSS Insight API)

| Attribute | Info |
|------|------|
| **API** | https://api.ossinsight.io/v1/trends/repos/?period=past_24_hours&language=All |
| **Trending Page** | https://github.com/trending?since=daily |
| **Focus Area** | AI/ML related trending repos |
| **Filter Criteria** | Composite score (stars + forks + PRs + pushes velocity), bottom 20% filtered |
| **Auth** | None required (free public API) |

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
| **r/MachineLearning** | https://reddit.com/r/MachineLearning | ML academic discussion |
| **r/LocalLLaMA** | https://reddit.com/r/LocalLLaMA | Open-source LLM community |
| **Filter Criteria** | Top upvoted posts within 24h |
| **Note** | Entity-specific subreddits (e.g. r/DeepSeek, r/ClaudeAI) are fetched per-entity via `Reddit Community` field |

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

