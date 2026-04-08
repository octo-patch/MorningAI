# Model & Infrastructure Tracking Agent

Entity registry for model providers and inference infrastructure platforms.


---

## Assigned Entity List

### 1. NVIDIA

| Attribute | Info |
|------|------|
| **X Official Account** | [@nvidia](https://x.com/nvidia), [@NVIDIAAIDev](https://x.com/NVIDIAAIDev) |
| **Key People** | [@DrJimFan](https://x.com/DrJimFan) - Jim Fan, Robotics Director |
| **Official Blog** | https://blogs.nvidia.com |
| **GitHub** | https://github.com/NVIDIA |
| **HuggingFace** | https://huggingface.co/nvidia |
| **arXiv** | https://arxiv.org/search/?query=NVIDIA+AI |

### 2. Mistral AI

| Attribute | Info |
|------|------|
| **X Official Account** | [@MistralAI](https://x.com/MistralAI) |
| **Key People** | [@arthurmensch](https://x.com/arthurmensch) - Arthur Mensch, CEO |
| **Official Blog** | https://mistral.ai/news |
| **Changelog** | https://docs.mistral.ai/getting-started/changelog |
| **GitHub** | https://github.com/mistralai |
| **HuggingFace** | https://huggingface.co/mistralai |
| **arXiv** | https://arxiv.org/search/?query=Mistral+AI |

### 3. Cohere

| Attribute | Info |
|------|------|
| **X Official Account** | [@cohere](https://x.com/cohere) |
| **Official Blog** | https://cohere.com/blog |
| **GitHub** | https://github.com/cohere-ai |
| **HuggingFace** | https://huggingface.co/CohereForAI |

### 4. Perplexity AI

| Attribute | Info |
|------|------|
| **X Official Account** | [@perplexity_ai](https://x.com/perplexity_ai) |
| **Key People** | [@AravSrinivas](https://x.com/AravSrinivas) - Aravind Srinivas, CEO<br>[@DenisYarats](https://x.com/DenisYarats) - Denis Yarats, CTO |
| **Official Blog** | https://www.perplexity.ai/hub/blog |

### 5. Amazon/AWS (AI)

| Attribute | Info |
|------|------|
| **X Official Account** | [@awscloud](https://x.com/awscloud) |
| **AI Blog** | https://aws.amazon.com/blogs/machine-learning/ |
| **Bedrock** | https://aws.amazon.com/bedrock/ |

### 6. Together AI

| Attribute | Info |
|------|------|
| **X Official Account** | [@togethercomputer](https://x.com/togethercomputer) |
| **Official Blog** | https://together.ai/blog |
| **GitHub** | https://github.com/togethercomputer |

### 7. Groq

| Attribute | Info |
|------|------|
| **X Official Account** | [@GroqInc](https://x.com/GroqInc) |
| **Official Blog** | https://wow.groq.com/blog/ |

### 8. Apple (MLX/AI)

| Attribute | Info |
|------|------|
| **ML Research Blog** | https://machinelearning.apple.com |
| **GitHub (MLX)** | https://github.com/ml-explore |
| **HuggingFace** | https://huggingface.co/apple |

---

## Workflow

### Input Parameters

- `date`: Working date (YYYY-MM-DD)
- `time_window_start` / `time_window_end`
- `output_dir`: Output directory path

### Execution Steps

#### Step 0: Reference Specification
Refer to `skills/tracking-list/SKILL.md` for tracking scope, scoring criteria, and timeliness check rules.

#### Step 1: Initialize Draft
Copy `templates/draft_collector.md` to `{output_dir}/draft_model-infra_{date}.md`

#### Step 2: Check Sources One by One

```
FOR each source in Checklist:
    1. Check source → Timeliness check → Cross-verification
    2. Classify and tag type label (Product/Model/Benchmark/Funding)
    3. Valid content → Append to corresponding type section
    4. Check Checkbox + Save Draft
END FOR
```

#### Step 3: Final Review
Confirm completion rate = 100%.

### Output Format

```json
{
  "status": "completed",
  "draft_path": "{output_dir}/draft_model-infra_{date}.md",
  "completion": {
    "total_sources": 25,
    "checked_sources": 25,
    "completion_rate": "100%"
  },
  "results": {
    "product": 0, "model": 0, "benchmark": 0, "funding": 0,
    "skipped": 0, "high_value_count": 0
  }
}
```
