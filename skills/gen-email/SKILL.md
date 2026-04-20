---
name: gen-email
version: "1.3.0"
description: Send the daily MorningAI digest as HTML email via SMTP to a configured recipient list.
---

## Objective

Distribute the daily AI news digest as **multipart HTML email** to a configured recipient list via SMTP. Reads the same `data_{DATE}.json` as `gen-message` (already scored, deduped, cross-source verified) and produces:

1. **HTML email body** — `email_{DATE}.html` (also used as the email body)
2. **Plain text fallback** — `email_{DATE}.txt` (multipart/alternative pairing)
3. **Send manifest** — `email_{DATE}_manifest.json` (per-recipient send status)

This is the **first true automated push channel** in the pipeline — gen-message / gen-social only generate files for manual sharing, while gen-email actually delivers to inboxes.

**Factual integrity inherited from gen-message:** every item must have a `source_url`. Items with score ≥ 7 must additionally satisfy `verified == true`. Drop items lacking a credible source.

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_ENABLED` | — | `false` | Master switch — when unset/false, the step is silently skipped |
| `EMAIL_RECIPIENTS` | ✓ | — | Comma-separated list, e.g. `alice@x.com,bob@y.com` |
| `EMAIL_RECIPIENTS_FILE` | — | `.claude/recipients.json` | Optional JSON file — overrides env list when present |
| `EMAIL_SMTP_HOST` | ✓ | — | SMTP server, e.g. `smtp.gmail.com`, `smtp.qq.com`, `smtp.163.com` |
| `EMAIL_SMTP_PORT` | — | `587` | Port (587=STARTTLS, 465=SSL, 25=plain) |
| `EMAIL_SMTP_TLS` | — | `starttls` | `starttls` / `ssl` / `none` |
| `EMAIL_SMTP_USER` | ✓ | — | SMTP auth username |
| `EMAIL_SMTP_PASSWORD` | ✓ | — | SMTP password (Gmail: use **App Password**, not account password) |
| `EMAIL_FROM` | — | `EMAIL_SMTP_USER` | Display sender, e.g. `MorningAI <noreply@x.com>` |
| `EMAIL_REPLY_TO` | — | — | Reply-To header |
| `EMAIL_SUBJECT_TEMPLATE` | — | `MorningAI {date} · {n} updates` | Subject template, supports `{date}` `{n}` `{lang}` |
| `EMAIL_LANG` | — | follows `--lang` | Email language: `zh` / `en` / `ja` |
| `EMAIL_MIN_SCORE` | — | `5` | Min `importance` score to include |
| `EMAIL_MAX_ITEMS` | — | `10` | Max items in the digest |
| `EMAIL_ATTACH_IMAGE` | — | `true` | Attach `message_{DATE}.png` if it exists |
| `EMAIL_RATE_LIMIT_DELAY` | — | `1` | Seconds to sleep between recipients (anti-throttling) |
| `EMAIL_LIST_UNSUBSCRIBE` | — | — | Unsubscribe target, e.g. `mailto:admin@x.com?subject=Unsubscribe` |
| `EMAIL_DRY_RUN` | — | `false` | If `true`, generate `email_*.html`/`email_*.txt` locally and **do not send** |

### Recipients JSON format (`EMAIL_RECIPIENTS_FILE`)

```json
[
  {"email": "alice@example.com", "name": "Alice", "lang": "zh", "min_score": 6, "active": true},
  {"email": "bob@example.com"},
  {"email": "paused@example.com", "active": false}
]
```

Per-recipient `lang` and `min_score` override the global defaults. Inactive entries are skipped.

---

## Content Selection Rules

Same as `gen-message` (see `skills/gen-message/SKILL.md` for full spec):

1. Load `data_{DATE}.json` from CWD.
2. Filter: `importance >= min_score` (per-recipient or global), `source_url` present, `verified == true` for score ≥ 7.
3. Apply category balance: `product` ≤ 4, `model` ≤ 3, `benchmark` ≤ 2, `financing` ≤ 2; overflow filled by score.
4. Sort by `importance` desc, cap at `EMAIL_MAX_ITEMS`.

---

## Workflow Summary

The `send_email.py` script handles all of the following automatically:

1. Read config, exit silently if `EMAIL_ENABLED != true`.
2. Validate required config (`EMAIL_SMTP_HOST` / `EMAIL_SMTP_USER` / `EMAIL_SMTP_PASSWORD` / recipients) — exit with clear error if missing.
3. Load `data_{DATE}.json` and apply selection rules.
4. Load recipients from `EMAIL_RECIPIENTS_FILE` (if exists) or `EMAIL_RECIPIENTS`.
5. Render preview using global `EMAIL_LANG` → write `email_{DATE}.html` and `email_{DATE}.txt`.
6. If `EMAIL_DRY_RUN=true`, exit after writing previews (no SMTP traffic).
7. Otherwise send to each recipient (re-render in their preferred language), sleeping `EMAIL_RATE_LIMIT_DELAY` seconds between sends.
8. Write `email_{DATE}_manifest.json` with per-recipient `status` (`sent` / `failed`) and `error` text.

### Invocation

The orchestrator (`skills/morning-ai/SKILL.md` Step 7) runs:

```bash
python3 skills/gen-email/scripts/send_email.py --date {YYYY-MM-DD}
```

Optional flags:
- `--date YYYY-MM-DD` — override the date (default: today UTC+8)
- `--data PATH` — override the data file path (default: `data_{DATE}.json` in CWD)
- `--lang zh|en|ja` — override `EMAIL_LANG`
- `--dry-run` — equivalent to `EMAIL_DRY_RUN=true`

---

## Compliance & Anti-Spam

- **List-Unsubscribe header (RFC 2369)** is automatically added when `EMAIL_LIST_UNSUBSCRIBE` is set. Major clients (Gmail, Outlook, Apple Mail) display a one-click unsubscribe button.
- **Plain-text fallback** is always included (multipart/alternative). Improves deliverability for clients that strip HTML.
- **Rate limiting** (`EMAIL_RATE_LIMIT_DELAY`) prevents tripping SMTP provider throttles (Gmail caps free accounts at ~100 sends/day, with short bursts blocked).
- **Per-recipient send** (no BCC) — protects subscriber privacy, allows per-recipient personalization (language), and avoids "looks like spam blast" heuristics.

When a recipient asks to unsubscribe, the admin manually removes them from `EMAIL_RECIPIENTS` or `recipients.json`. Self-service unsubscribe requires a hosted backend (out of scope for this skill).

---

## Common SMTP Configurations

See `docs/email-setup.md` for full details. Quick reference:

| Provider | Host | Port | TLS | Notes |
|----------|------|------|-----|-------|
| Gmail | `smtp.gmail.com` | 587 | STARTTLS | Requires **App Password** (turn on 2FA → generate App Password) |
| QQ Mail | `smtp.qq.com` | 465 | SSL | Use authorization code, not login password |
| 163 Mail | `smtp.163.com` | 465 | SSL | Use authorization code |
| Outlook | `smtp.office365.com` | 587 | STARTTLS | Account password or App Password |
| 阿里云企业邮 | `smtp.qiye.aliyun.com` | 465 | SSL | Account password |

---

## Example: Manifest Output

```json
{
  "date": "2026-04-20",
  "subject": "MorningAI 2026-04-20 · 8 updates",
  "total": 3,
  "succeeded": 2,
  "failed": 1,
  "results": [
    {"email": "alice@example.com", "status": "sent", "message_id": "<...@morning-ai>"},
    {"email": "bob@example.com",   "status": "sent", "message_id": "<...@morning-ai>"},
    {"email": "carol@example.com", "status": "failed", "error": "smtp error: 550 mailbox unavailable"}
  ]
}
```

The manifest enables retry logic in future runs (skip already-`sent` recipients) and makes failures visible without scraping logs.
