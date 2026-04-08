# AI Apps & Platform Tracking Agent

Entity registry for AI app-building platforms and consumer AI products.


---

## Assigned Entity List

### 1. v0 (Vercel)

| Attribute | Info |
|------|------|
| **X Official Account** | [@v0](https://x.com/v0) |
| **Key People** | [@rauchg](https://x.com/rauchg) - Guillermo Rauch, Vercel CEO |
| **Vercel Changelog** | https://vercel.com/changelog |

### 2. bolt.new

| Attribute | Info |
|------|------|
| **X Official Account** | [@boltdotnew](https://x.com/boltdotnew) |
| **Key People** | [@EricSimons](https://x.com/EricSimons) - Eric Simons, StackBlitz CEO |
| **Release Notes** | https://support.bolt.new/release-notes |

### 3. Lovable

| Attribute | Info |
|------|------|
| **X Official Account** | [@Lovable](https://x.com/Lovable) |
| **Key People** | [@antonosika](https://x.com/antonosika) - Anton Osika, CEO<br>[@felixhhaas](https://x.com/felixhhaas) - Felix Haas, Co-founder |
| **Changelog** | https://lovable.dev/changelog |

### 4. Replit

| Attribute | Info |
|------|------|
| **X Official Account** | [@Replit](https://x.com/Replit) |
| **Key People** | [@amasad](https://x.com/amasad) - Amjad Masad, CEO |
| **Changelog** | https://docs.replit.com/updates |

### 5. Lovart

| Attribute | Info |
|------|------|
| **X Official Account** | [@lovart_ai](https://x.com/lovart_ai) |
| **Key People** | [@Elena_Leung_29](https://x.com/Elena_Leung_29) - Elena Leung, COO |
| **Changelog** | https://www.lovart.ai/changelog |

### 6. Manus

| Attribute | Info |
|------|------|
| **X Official Account** | [@ManusAI](https://x.com/ManusAI) |
| **Key People** | [@Red_Xiao_](https://x.com/Red_Xiao_) - Red Xiao, CEO<br>[@pelotonben](https://x.com/pelotonben) - Yichao Peak Ji, Co-founder |

### 7. Genspark

| Attribute | Info |
|------|------|
| **X Official Account** | [@genspark_ai](https://x.com/genspark_ai) |
| **Key People** | [@ericjing_ai](https://x.com/ericjing_ai) - Eric Jing, CEO<br>[@sang_wen](https://x.com/sang_wen) - Wen Sang, COO |
| **Changelog** | https://www.genspark.ai/docs/ai_slides_changelog |

### 8. Character.ai

| Attribute | Info |
|------|------|
| **X Official Account** | [@character_ai](https://x.com/character_ai) |
| **Official Website** | https://character.ai |

---

## Workflow

### Input Parameters

- `date`, `time_window_start`, `time_window_end`, `output_dir`

### Execution Steps

#### Step 0: Reference Specification
Refer to `skills/tracking-list/SKILL.md` for tracking scope, scoring criteria, and timeliness check rules.

#### Step 1: Initialize Draft
Copy `templates/draft_collector.md` to `{output_dir}/draft_ai-apps_{date}.md`

#### Step 2: Check Sources One by One

```
FOR each source in Checklist:
    1. Check source -> timeliness check -> verify
    2. Classify and tag type labels (mainly "Product" and "Funding")
    3. Key people post -> must cross-verify with Changelog
    4. Tips sharing (not new features) -> skip
    5. Valid content -> append to corresponding type section
    6. Check Checkbox + save Draft
END FOR
```

#### Step 3: Final Review
Confirm completion rate = 100%.

### Output Format

```json
{
  "status": "completed",
  "draft_path": "{output_dir}/draft_ai-apps_{date}.md",
  "completion": {
    "total_sources": 20,
    "checked_sources": 20,
    "completion_rate": "100%"
  },
  "results": {
    "product": 0, "model": 0, "benchmark": 0, "funding": 0,
    "skipped": 0, "high_value_count": 0
  }
}
```
