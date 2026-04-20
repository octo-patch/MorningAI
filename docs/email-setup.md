# Email Setup Guide

Step-by-step SMTP configuration for the most common providers. After setting these env vars in `~/.config/morning-ai/.env` (or your project's `.env`), `EMAIL_ENABLED=true` is all you need to enable the email subscription step.

> **Test before going live**: set `EMAIL_DRY_RUN=true` first. The script will write `email_{date}.html` and `email_{date}.txt` locally without sending anything. Open the HTML in a browser to verify rendering.

---

## Gmail

Gmail requires an **App Password** — your normal Google account password will not work.

### 1. Enable 2-Step Verification
https://myaccount.google.com/security → "2-Step Verification" → turn on.

### 2. Generate an App Password
https://myaccount.google.com/apppasswords → name it "MorningAI" → copy the 16-character password (shown without spaces, e.g. `abcdefghijklmnop`).

### 3. Configure
```env
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_TLS=starttls
EMAIL_SMTP_USER=you@gmail.com
EMAIL_SMTP_PASSWORD=abcdefghijklmnop
EMAIL_FROM=MorningAI <you@gmail.com>
EMAIL_RECIPIENTS=you@gmail.com,team@example.com
```

### Quotas
- Free Gmail: ~100–500 sends/day, with bursts capped (set `EMAIL_RATE_LIMIT_DELAY=2` for safety).
- Workspace: ~2,000/day.

---

## QQ Mail (QQ 邮箱)

QQ Mail requires an **authorization code** (授权码) — not the QQ login password.

### 1. Enable SMTP service
登录 QQ 邮箱网页版 → 设置 → 账户 → 找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务" → 开启 "IMAP/SMTP 服务"。

### 2. Generate authorization code
按系统提示发送验证短信 → 获取 16 位授权码（如 `xxxxxxxxxxxxxxxx`）。

### 3. Configure
```env
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.qq.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_TLS=ssl
EMAIL_SMTP_USER=you@qq.com
EMAIL_SMTP_PASSWORD=xxxxxxxxxxxxxxxx
EMAIL_FROM=MorningAI <you@qq.com>
EMAIL_RECIPIENTS=you@qq.com
```

> Tip: 端口 465（SSL）比 587（STARTTLS）在 QQ 邮箱上更稳定。

---

## 163 Mail (网易 163 邮箱)

163 同样需要 **授权码**。

### 1. Enable SMTP service
登录 mail.163.com → 设置 → POP3/SMTP/IMAP → 开启 "IMAP/SMTP 服务"。

### 2. 获取授权码
按提示发送短信 → 获取授权码。

### 3. Configure
```env
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.163.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_TLS=ssl
EMAIL_SMTP_USER=you@163.com
EMAIL_SMTP_PASSWORD=xxxxxxxxxxxxxxxx
EMAIL_FROM=MorningAI <you@163.com>
EMAIL_RECIPIENTS=you@163.com
```

---

## Outlook / Microsoft 365

```env
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.office365.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_TLS=starttls
EMAIL_SMTP_USER=you@outlook.com
EMAIL_SMTP_PASSWORD=your-password-or-app-password
EMAIL_FROM=MorningAI <you@outlook.com>
```

> If 2FA is enabled on your Microsoft account, generate an [App Password](https://account.microsoft.com/security) and use it instead of your account password.

---

## 阿里云企业邮 (Alibaba Cloud Enterprise Mail)

```env
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.qiye.aliyun.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_TLS=ssl
EMAIL_SMTP_USER=you@yourcompany.com
EMAIL_SMTP_PASSWORD=your-mailbox-password
EMAIL_FROM=MorningAI <you@yourcompany.com>
```

---

## Recipients File (Optional)

If you have more than ~5 recipients or need per-recipient settings, create `.claude/recipients.json`:

```json
[
  {"email": "alice@example.com", "name": "Alice", "lang": "zh", "min_score": 6, "active": true},
  {"email": "bob@example.com",   "name": "Bob",   "lang": "en"},
  {"email": "charlie@example.com", "active": false}
]
```

Fields:
- `email` (required) — recipient address
- `name` — display name (used in the To header)
- `lang` — `zh` / `en` / `ja`, overrides global `EMAIL_LANG`
- `min_score` — overrides global `EMAIL_MIN_SCORE` (e.g. send only score ≥ 7 to executives)
- `active` — set `false` to pause without removing the entry

When `EMAIL_RECIPIENTS_FILE` exists, it **overrides** the env list. The default path is `.claude/recipients.json` (gitignored).

---

## Subject & Unsubscribe

```env
# Custom subject template — placeholders: {date}, {n}, {lang}
EMAIL_SUBJECT_TEMPLATE=MorningAI 早报 {date}（{n} 条）

# Unsubscribe target — appears in footer + List-Unsubscribe header.
# Mainstream clients (Gmail, Outlook) show a one-click unsubscribe button.
EMAIL_LIST_UNSUBSCRIBE=mailto:admin@example.com?subject=Unsubscribe-MorningAI
```

When a recipient asks to unsubscribe, manually remove them from `EMAIL_RECIPIENTS` or set `"active": false` in `recipients.json`.

---

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| `connection error: [Errno 111] Connection refused` | Port blocked by your network/firewall — try 465 with `EMAIL_SMTP_TLS=ssl` |
| `smtp error: 535 5.7.8 Authentication failed` | Wrong password — Gmail/QQ/163 require app password, not account password |
| `smtp error: 530 5.7.0 Must issue a STARTTLS command first` | Set `EMAIL_SMTP_TLS=starttls` |
| `smtp error: 550 5.7.1 ... Daily user sending quota exceeded` | Hit Gmail/Outlook rate limit — increase `EMAIL_RATE_LIMIT_DELAY` and reduce recipient count, or wait 24h |
| Email lands in spam folder | Add `EMAIL_LIST_UNSUBSCRIBE`, configure SPF/DKIM on your sending domain (Workspace / 企业邮 only), and avoid spam-trigger words in subject |
| `[gen-email] no active recipients` | `EMAIL_RECIPIENTS` not set, or all entries in `recipients.json` have `active: false` |

Run with `EMAIL_DRY_RUN=true` to debug content/template issues without involving SMTP at all.
