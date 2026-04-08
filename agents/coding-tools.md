# Coding Tools Product Tracking Agent

Entity registry for AI coding tools and developer assistant platforms (tools under major labs such as Claude Code, Codex CLI, GitHub Copilot are handled by the ai-labs group).

---

## Assigned Entity List

### 1. Cursor

| Attribute | Info |
|------|------|
| **X Official Account** | [@cursor_ai](https://x.com/cursor_ai) |
| **Key People** | [@mntruell](https://x.com/mntruell) - Michael Truell, CEO<br>[@ericzakariasson](https://x.com/ericzakariasson) - Eric Zakariasson |
| **Changelog** | https://cursor.com/changelog |

### 2. Cline

| Attribute | Info |
|------|------|
| **X Official Account** | [@cline](https://x.com/cline) |
| **Key People** | [@sdrzn](https://x.com/sdrzn) - Saoud Rizwan, CEO<br>[@nickbaumann_](https://x.com/nickbaumann_) - Nick Baumann |
| **GitHub Releases** | https://github.com/cline/cline/releases |

### 3. OpenCode

| Attribute | Info |
|------|------|
| **Key People** | [@thdxr](https://x.com/thdxr) - Dax Raad, Founder<br>[@fanjiewang](https://x.com/fanjiewang) - Fanjie Wang |
| **GitHub Releases** | https://github.com/sst/opencode/releases |

### 4. Droid (Factory AI)

| Attribute | Info |
|------|------|
| **X Official Account** | [@FactoryAI](https://x.com/FactoryAI) |
| **CLI Changelog** | https://docs.factory.ai/changelog/cli-updates |

### 5. OpenClaw (formerly Clawd/Moltbot)

| Attribute | Info |
|------|------|
| **X Official Account** | [@openclaw](https://x.com/openclaw) |
| **Key People** | [@steipete](https://x.com/steipete) - Peter Steinberger, Founder |
| **Official Website** | https://openclaw.ai |
| **Docs** | https://docs.openclaw.ai |
| **Blog** | https://openclaws.io/blog |
| **Changelog** | https://openclawai.io/changelog |
| **GitHub** | https://github.com/openclaw/openclaw |
| **GitHub Releases** | https://github.com/openclaw/openclaw/releases |

### 6. Windsurf (Codeium)

| Attribute | Info |
|------|------|
| **X Official Account** | [@windsurf](https://x.com/windsurf) |
| **Official Blog** | https://windsurf.com/blog |
| **Changelog** | https://windsurf.com/changelog |

### 7. Augment Code

| Attribute | Info |
|------|------|
| **X Official Account** | [@AugmentCode](https://x.com/AugmentCode) |
| **Official Blog** | https://www.augmentcode.com/blog |

### 8. Aider

| Attribute | Info |
|------|------|
| **Key People** | Paul Gauthier, Creator |
| **Official Website** | https://aider.chat |
| **GitHub** | https://github.com/Aider-AI/aider |
| **GitHub Releases** | https://github.com/Aider-AI/aider/releases |

### 9. Devin (Cognition)

| Attribute | Info |
|------|------|
| **X Official Account** | [@cognition](https://x.com/cognition) |
| **Official Blog** | https://cognition.ai/blog |

### 10. browser-use

| Attribute | Info |
|------|------|
| **X Official Account** | [@browser_use](https://x.com/browser_use) |
| **Key People** | [@gregpr07](https://x.com/gregpr07), [@larsencc](https://x.com/larsencc) |
| **Official Website** | https://browser-use.com |
| **Changelog** | https://browser-use.com/changelog |
| **GitHub** | https://github.com/browser-use/browser-use |
| **GitHub Releases** | https://github.com/browser-use/browser-use/releases |

---

## Workflow

### Input Parameters

- `date`, `time_window_start`, `time_window_end`, `output_dir`

### Execution Steps

#### Step 0: Reference Specification
Refer to `skills/tracking-list/SKILL.md` for tracking scope, scoring criteria, and timeliness check rules.

#### Step 1: Initialize Draft
Copy `templates/draft_collector.md` to `{output_dir}/draft_coding-tools_{date}.md`

#### Step 2: Check Sources One by One

```
FOR each source in Checklist:
    1. Check source → Timeliness check → Cross-verification
    2. Classify and tag type label (mainly "Product" and "Funding")
    3. Key people post → must cross-verify with Changelog
    4. Tips sharing (not new features) → skip
    5. Valid content → Append to corresponding type section
    6. Check Checkbox + Save Draft
END FOR
```

#### Step 3: Final Review
Confirm completion rate = 100%.

### Output Format

```json
{
  "status": "completed",
  "draft_path": "{output_dir}/draft_coding-tools_{date}.md",
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
