# Benchmarks & Academic Tracking Agent

Entity registry for benchmark organizations, opinion leaders, academic research channels, and industry media.


---

## Assigned Entity List

### Benchmark Organizations

| Name | X Account | Website | Description |
|------|--------|------|------|
| LMSYS Chatbot Arena | [@laboramsys](https://x.com/laboramsys) | https://lmsys.org | Chatbot Arena / VLM Arena |
| LMArena | [@arena](https://x.com/arena) | - | Model battle ranking |
| Artificial Analysis | [@ArtificialAnlys](https://x.com/ArtificialAnlys) | https://artificialanalysis.ai | Model speed/quality comparison |
| HuggingFace Open LLM | [@huggingface](https://x.com/huggingface) | https://huggingface.co/spaces/open-llm-leaderboard | Open-source model leaderboard |
| Scale AI SEAL | [@scale_AI](https://x.com/scale_AI) | https://scale.com/leaderboard | Scale Benchmark |
| OpenCompass | - | https://opencompass.org.cn | Multimodal benchmark |
| vLLM | [@vllm_project](https://x.com/vllm_project) | - | Inference performance |
| LiveBench | - | https://livebench.ai | Real-time benchmark |
| WildBench | - | https://huggingface.co/spaces/allenai/WildBench | Allen AI Benchmark |

### Additional Benchmark Sources

| Name | X Account | Description |
|------|--------|------|
| HuggingFace | [@huggingface](https://x.com/huggingface) | Model releases, trends |
| Replicate | [@replicate](https://x.com/replicate) | Model deployment, trends |

### Key Opinion Leaders (KOL)

| Name | X Account | Description |
|------|--------|------|
| Andrej Karpathy | [@karpathy](https://x.com/karpathy) | Former Tesla AI / OpenAI founding member |
| AK (Paper digest) | [@_akhaliq](https://x.com/_akhaliq) | Real-time AI paper releases, HuggingFace member |
| Andrew Ng | [@AndrewYNg](https://x.com/AndrewYNg) | AI pioneer |
| Rowan Cheung | [@rowancheung](https://x.com/rowancheung) | The Rundown AI Founder |
| Ben Tossell | [@bentossell](https://x.com/bentossell) | Ben's Bites Founder |
| Elie Bakouch | [@eliebakouch](https://x.com/eliebakouch) | AI news blogger |
| Swyx | [@swyx](https://x.com/swyx) | Latent Space Host, AI engineering advocate |
| Simon Willison | [@simonw](https://x.com/simonw) | Django Co-creator, in-depth AI tool reviews |

> **Note**: KOL information must be traced back to official channels for confirmation, cannot be used directly as a primary source

### Paper Channels

| Name | URL | Type |
|------|-----|------|
| Papers with Code | https://paperswithcode.com | Papers + Code |
| HuggingFace Papers | https://huggingface.co/papers | Daily trending papers |
| arXiv cs.LG | https://arxiv.org/list/cs.LG/recent | Machine Learning |
| arXiv cs.CL | https://arxiv.org/list/cs.CL/recent | Natural Language Processing |
| arXiv cs.CV | https://arxiv.org/list/cs.CV/recent | Computer Vision |

### Community Discussions

| Name | URL | Type |
|------|-----|------|
| Reddit r/MachineLearning | https://reddit.com/r/MachineLearning | ML academic discussion |
| Reddit r/LocalLLaMA | https://reddit.com/r/LocalLLaMA | Open-source LLM community |

### Industry Media (for lead discovery only, must trace to source)

| Name | URL |
|------|-----|
| VentureBeat AI | https://venturebeat.com/ai |
| The Decoder | https://the-decoder.com |
| Ars Technica AI | https://arstechnica.com/ai |
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/ |

---

## Deduplication Notes

This Agent focuses on **cross-vendor** benchmarks/papers/trends. The following content is covered by other Agents, this Agent skips:

- Specific vendor model/product updates -> covered by corresponding vendor Agent
- Vendor-specific technical papers -> if papers are from OpenAI/Anthropic etc., covered by ai-labs etc. Agent
- This Agent only focuses on: independent benchmark results, cross-vendor comparisons, general academic research, open-source community updates, industry trends

---

## Workflow

### Input Parameters

- `date`, `time_window_start`, `time_window_end`, `output_dir`

### Execution Steps

#### Step 0: Reference Specification
Refer to `skills/tracking-list/SKILL.md` for tracking scope, scoring criteria, and timeliness check rules.

#### Step 1: Initialize Draft
Copy `templates/draft_collector.md` to `{output_dir}/draft_benchmarks-academic_{date}.md`

#### Step 2: Leaderboard Change Detection

Actively check each leaderboard for new model entries and ranking changes. Uses **two complementary methods**: change signal detection + snapshot diff.

##### Method A: Change Signals

```
FOR each leaderboard in Benchmark Organizations:
    1. Check change signals (in priority order):
       a. Changelog / update log on the leaderboard site (e.g. LMSYS blog, HF space commit history)
       b. X/Twitter posts from the leaderboard's official account announcing new models or ranking updates
       c. Leaderboard "recent additions" or "last updated" section, if available
    2. For each detected change:
       - Confirm the date of first appearance / ranking change (NOT current access date)
       - Timeliness check against [time_window_start, time_window_end)
       - Record as Benchmark type with Event Type = "Leaderboard change" or "New model entry"
       - Include anonymous / unnamed models if announced (e.g. mystery models in Chatbot Arena)
    3. Check Checkbox + save Draft
END FOR
```

##### Method B: Snapshot Diff (automated detection)

After extracting the current leaderboard state, save a snapshot and diff against the previous one to catch changes that lack explicit announcements.

```
FOR each leaderboard in Benchmark Organizations:
    1. Extract current top models from the leaderboard (model name, rank, score)
    2. Call snapshot tool:
       python3 scripts/leaderboard_snapshot.py save \
         --leaderboard {leaderboard_id} \
         --date {date} \
         --data '[{"model":"...","rank":N,"score":X.X}, ...]'
    3. Read the JSON output:
       - new_models → record each as Event Type = "New model entry"
       - rank_changes → record significant moves as Event Type = "Leaderboard change"
       - score_changes → note if meaningful
       - is_initial = true → first run, skip diff (all entries are baseline)
    4. Deduplicate against Method A results (don't record the same change twice)
END FOR
```

> **Leaderboard IDs**: Use lowercase, e.g. `lmsys`, `lmarena`, `artificial_analysis`, `hf_open_llm`, `scale_seal`, `opencompass`, `livebench`, `wildbench`

| Leaderboard | What to check | URL |
|-------------|--------------|-----|
| LMSYS Chatbot Arena | New models entering arena, Elo ranking shifts | https://lmsys.org |
| LMArena | New battle results, ranking changes | @arena on X |
| Artificial Analysis | New models benchmarked, quality/speed ranking changes | https://artificialanalysis.ai |
| HuggingFace Open LLM | New model submissions, score changes in top ranks | https://huggingface.co/spaces/open-llm-leaderboard |
| Scale AI SEAL | New evaluation results, ranking updates | https://scale.com/leaderboard |
| OpenCompass | New multimodal benchmark entries | https://opencompass.org.cn |
| LiveBench | New real-time evaluation results | https://livebench.ai |
| WildBench | New model evaluations | https://huggingface.co/spaces/allenai/WildBench |

> **Key**: A model "currently on the list" does NOT mean it was "just added". Always verify the date of first entry via changelog, announcement, or X post.

#### Step 3: Check Remaining Sources

```
FOR each source in Checklist (excluding leaderboards already checked):
    1. Check source -> timeliness check
    2. Classify and tag type labels (mainly "Benchmark")
    3. KOL info -> must trace to official channels
    4. Valid content -> append to corresponding type section
    6. Check Checkbox + save Draft
END FOR
```

#### Step 4: Final Review
Confirm completion rate = 100%.

### Output Format

```json
{
  "status": "completed",
  "draft_path": "{output_dir}/draft_benchmarks-academic_{date}.md",
  "completion": {
    "total_sources": 30,
    "checked_sources": 30,
    "completion_rate": "100%"
  },
  "results": {
    "product": 0, "model": 0, "benchmark": 0, "funding": 0,
    "skipped": 0, "high_value_count": 0
  }
}
```
