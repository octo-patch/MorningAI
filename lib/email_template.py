"""Email template rendering (HTML + plain text + subject).

Zero external dependencies — uses stdlib `string.Template` and `html.escape`.
HTML uses inline CSS and table-based layout for maximum email-client compatibility
(Gmail, Outlook, QQ Mail, Apple Mail, etc.).
"""

import html
from string import Template
from typing import Any, Dict, List, Optional


# Language-specific text snippets (mirrors gen-message templates/digest.md)
LANG_TEXT = {
    "zh": {
        "header_count": "共 {n} 条重要更新",
        "footer": "Powered by MorningAI · 完整报告: report_{date}.md",
        "unsubscribe_label": "退订",
        "unsubscribe_hint": "如需退订，请回复此邮件或联系",
        "no_items": "今日暂无符合条件的更新。",
        "kol_section_title": "KOL 观点",
        "kol_no_items": "今日 KOL 安静，暂无独立观点。",
    },
    "en": {
        "header_count": "{n} notable updates today",
        "footer": "Powered by MorningAI · Full report: report_{date}.md",
        "unsubscribe_label": "Unsubscribe",
        "unsubscribe_hint": "To unsubscribe, reply to this email or contact",
        "no_items": "No qualifying updates today.",
        "kol_section_title": "KOL Voices",
        "kol_no_items": "Today's KOL voices were quiet — no independent commentary.",
    },
    "ja": {
        "header_count": "本日の注目 {n} 件",
        "footer": "Powered by MorningAI · 完全レポート: report_{date}.md",
        "unsubscribe_label": "配信停止",
        "unsubscribe_hint": "配信を停止するには、このメールに返信するか以下にご連絡ください",
        "no_items": "本日該当する更新はありません。",
        "kol_section_title": "KOL の声",
        "kol_no_items": "本日 KOL は静かでした — 独自の見解はありません。",
    },
}


# Score → emoji marker (mirrors gen-message)
def _emoji_for_score(score: float) -> str:
    if score >= 9:
        return "🔥"
    if score >= 7:
        return "⭐"
    return "🔷"


def _safe_lang(lang: Optional[str]) -> str:
    return lang if lang in LANG_TEXT else "en"


def _strip_mailto(unsubscribe: str) -> str:
    """Extract email address from 'mailto:foo@bar?subject=...' for display."""
    if not unsubscribe:
        return ""
    addr = unsubscribe[len("mailto:"):] if unsubscribe.startswith("mailto:") else unsubscribe
    return addr.split("?", 1)[0]


# ---------- Subject ----------

def render_subject(template: str, date: str, n: int, lang: str = "en") -> str:
    """Render email subject. Supports {date}, {n}, {lang} placeholders.

    Default template (caller-provided): "MorningAI {date} · {n} updates"
    """
    if not template:
        template = "MorningAI {date} · {n} updates"
    try:
        return template.format(date=date, n=n, lang=lang)
    except (KeyError, IndexError):
        # Bad template — fall back to safe default
        return f"MorningAI {date} · {n} updates"


# ---------- Plain text ----------

_TEXT_ITEM = """{emoji} {entity_event}
{summary}
🔗 {url}
"""


def render_text(items: List[Dict[str, Any]], date: str, lang: str = "en",
                unsubscribe: str = "",
                kol_items: Optional[List[Dict[str, Any]]] = None,
                show_kol_section: bool = False) -> str:
    """Render plain-text email body. Mirrors gen-message digest format.

    `items` is a list of dicts with keys: entity, title, summary, importance, source_url.
    `kol_items` is an optional list of items where `is_kol_voice == true`. When
    `show_kol_section` is true, a `KOL Voices` block is appended after the main
    items — populated with `kol_items` if any, otherwise an empty-state line so
    subscribers know the section is alive on quiet KOL days.
    """
    lang = _safe_lang(lang)
    t = LANG_TEXT[lang]

    lines = [f"MorningAI {date}", "", t["header_count"].format(n=len(items)), ""]

    if not items:
        lines.append(t["no_items"])
    else:
        for item in items:
            entity = item.get("entity", "").strip()
            title = item.get("title", "").strip()
            # If title already starts with entity, don't duplicate it
            if entity and not title.lower().startswith(entity.lower()):
                head = f"{entity} {title}".strip()
            else:
                head = title or entity
            block = _TEXT_ITEM.format(
                emoji=_emoji_for_score(item.get("importance", 0)),
                entity_event=head,
                summary=item.get("summary", "").strip(),
                url=item.get("source_url", "").strip(),
            )
            lines.append(block)

    if show_kol_section:
        lines.append("")
        lines.append(f"── {t['kol_section_title']} ──")
        lines.append("")
        if kol_items:
            for item in kol_items:
                entity = item.get("entity", "").strip()
                title = item.get("title", "").strip()
                if entity and not title.lower().startswith(entity.lower()):
                    head = f"{entity} {title}".strip()
                else:
                    head = title or entity
                block = _TEXT_ITEM.format(
                    emoji="🎙️",
                    entity_event=head,
                    summary=item.get("summary", "").strip(),
                    url=item.get("source_url", "").strip(),
                )
                lines.append(block)
        else:
            lines.append(t["kol_no_items"])
            lines.append("")

    lines.append("---")
    lines.append(t["footer"].format(date=date))

    if unsubscribe:
        addr = _strip_mailto(unsubscribe)
        lines.append("")
        lines.append(f"{t['unsubscribe_hint']} {addr}")

    return "\n".join(lines)


# ---------- HTML ----------

# Inline CSS, table-based layout. Tested patterns from major email clients.
# Color palette aligned with gen-infographic "classic" style.
_HTML_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="$lang">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>$subject</title>
</head>
<body style="margin:0;padding:0;background:#f4f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#1f2937;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:24px 0;">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.06);overflow:hidden;">
<tr><td style="background:linear-gradient(135deg,#1e40af,#7c3aed);padding:24px 32px;color:#ffffff;">
<div style="font-size:22px;font-weight:700;letter-spacing:-0.01em;">MorningAI</div>
<div style="font-size:14px;opacity:0.85;margin-top:4px;">$date · $count_label</div>
</td></tr>
<tr><td style="padding:24px 32px;">
$items_html
</td></tr>
<tr><td style="padding:16px 32px 24px;border-top:1px solid #e5e7eb;font-size:12px;color:#6b7280;line-height:1.6;">
<div>$footer</div>
$unsubscribe_html
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>
""")


_HTML_ITEM = Template("""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:18px;border-left:3px solid $accent;padding-left:14px;">
<tr><td>
<div style="font-size:15px;font-weight:600;line-height:1.4;color:#111827;">$emoji $head</div>
<div style="font-size:14px;line-height:1.6;color:#374151;margin-top:6px;">$summary</div>
<div style="margin-top:6px;"><a href="$url" style="color:#2563eb;text-decoration:none;font-size:13px;word-break:break-all;">🔗 $url_display</a></div>
</td></tr>
</table>""")


def _accent_for_score(score: float) -> str:
    if score >= 9:
        return "#dc2626"   # red — fire
    if score >= 7:
        return "#f59e0b"   # amber — star
    return "#3b82f6"       # blue — diamond


def render_html(items: List[Dict[str, Any]], date: str, lang: str = "en",
                subject: str = "", unsubscribe: str = "",
                kol_items: Optional[List[Dict[str, Any]]] = None,
                show_kol_section: bool = False) -> str:
    """Render HTML email body. All user data is HTML-escaped.

    `kol_items` and `show_kol_section` mirror `render_text` — when
    `show_kol_section` is true, a KOL Voices block is appended after the main
    items, populated with `kol_items` if any, otherwise an empty-state line.
    """
    lang = _safe_lang(lang)
    t = LANG_TEXT[lang]

    if items:
        item_blocks = []
        for item in items:
            entity = item.get("entity", "").strip()
            title = item.get("title", "").strip()
            if entity and not title.lower().startswith(entity.lower()):
                head = f"{entity} {title}".strip()
            else:
                head = title or entity
            url = item.get("source_url", "").strip()
            url_display = url if len(url) <= 60 else url[:57] + "…"
            item_blocks.append(_HTML_ITEM.substitute(
                emoji=_emoji_for_score(item.get("importance", 0)),
                accent=_accent_for_score(item.get("importance", 0)),
                head=html.escape(head),
                summary=html.escape(item.get("summary", "").strip()),
                url=html.escape(url, quote=True),
                url_display=html.escape(url_display),
            ))
        items_html = "\n".join(item_blocks)
    else:
        items_html = (
            f'<p style="color:#6b7280;font-size:14px;">{html.escape(t["no_items"])}</p>'
        )

    if show_kol_section:
        items_html += _render_kol_html(kol_items or [], t)

    if unsubscribe:
        addr = _strip_mailto(unsubscribe)
        unsubscribe_html = (
            f'<div style="margin-top:8px;">'
            f'{html.escape(t["unsubscribe_hint"])} '
            f'<a href="{html.escape(unsubscribe, quote=True)}" '
            f'style="color:#6b7280;">{html.escape(addr)}</a></div>'
        )
    else:
        unsubscribe_html = ""

    return _HTML_TEMPLATE.substitute(
        lang=lang,
        subject=html.escape(subject or f"MorningAI {date}"),
        date=html.escape(date),
        count_label=html.escape(t["header_count"].format(n=len(items))),
        items_html=items_html,
        footer=html.escape(t["footer"].format(date=date)),
        unsubscribe_html=unsubscribe_html,
    )


# KOL section uses a teal accent (#0d9488) to visually distinguish independent
# commentary from the main news items. The 🎙️ marker mirrors gen-infographic
# / gen-social conventions where KOL voices are rendered as a separate class
# rather than mixed in with vendor announcements.
_HTML_KOL_HEADER = Template("""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0 12px;border-top:1px solid #e5e7eb;">
<tr><td style="padding-top:16px;">
<div style="font-size:13px;font-weight:600;letter-spacing:0.04em;color:#0d9488;text-transform:uppercase;">🎙️ $title</div>
</td></tr>
</table>""")


_HTML_KOL_ITEM = Template("""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;border-left:3px solid #0d9488;padding-left:14px;">
<tr><td>
<div style="font-size:14px;font-weight:600;line-height:1.4;color:#111827;">🎙️ $head</div>
<div style="font-size:13px;line-height:1.6;color:#374151;margin-top:4px;">$summary</div>
<div style="margin-top:4px;"><a href="$url" style="color:#0d9488;text-decoration:none;font-size:12px;word-break:break-all;">🔗 $url_display</a></div>
</td></tr>
</table>""")


def _render_kol_html(kol_items: List[Dict[str, Any]], t: Dict[str, str]) -> str:
    """Render the KOL section block (header + items or empty-state)."""
    parts = [_HTML_KOL_HEADER.substitute(title=html.escape(t["kol_section_title"]))]
    if not kol_items:
        parts.append(
            f'<p style="color:#6b7280;font-size:13px;font-style:italic;">'
            f'{html.escape(t["kol_no_items"])}</p>'
        )
        return "\n".join(parts)
    for item in kol_items:
        entity = item.get("entity", "").strip()
        title = item.get("title", "").strip()
        if entity and not title.lower().startswith(entity.lower()):
            head = f"{entity} {title}".strip()
        else:
            head = title or entity
        url = item.get("source_url", "").strip()
        url_display = url if len(url) <= 60 else url[:57] + "…"
        parts.append(_HTML_KOL_ITEM.substitute(
            head=html.escape(head),
            summary=html.escape(item.get("summary", "").strip()),
            url=html.escape(url, quote=True),
            url_display=html.escape(url_display),
        ))
    return "\n".join(parts)
