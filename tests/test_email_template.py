"""Tests for lib/email_template.py — HTML / text / subject rendering."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.email_template import render_html, render_subject, render_text


SAMPLE_ITEMS = [
    {
        "entity": "Anthropic",
        "title": "Claude 4.5 Sonnet released",
        "summary": "New mid-tier model with +18% SWE-Bench, 200K context.",
        "importance": 9.2,
        "source_url": "https://anthropic.com/news/claude-4-5",
        "content_type": "model",
        "verified": True,
    },
    {
        "entity": "Cursor",
        "title": "Background Agents GA",
        "summary": "Autonomous agents for multi-file refactoring.",
        "importance": 7.5,
        "source_url": "https://cursor.com/changelog",
        "content_type": "product",
        "verified": True,
    },
    {
        "entity": "Windsurf",
        "title": "Series C $200M",
        "summary": "Largest round in coding tools space.",
        "importance": 5.5,
        "source_url": "https://example.com/windsurf",
        "content_type": "financing",
        "verified": False,
    },
]


SAMPLE_KOL_ITEMS = [
    {
        "entity": "@karpathy",
        "title": "On the future of agents",
        "summary": "Long-form take on tool-use vs RL: agents will plateau without grounded environments.",
        "importance": 6.5,
        "source_url": "https://x.com/karpathy/status/123",
        "is_kol_voice": True,
    },
    {
        "entity": "@simonw",
        "title": "Why I stopped self-hosting LLMs",
        "summary": "Cost analysis: API pricing has dropped enough that self-hosting only makes sense at scale.",
        "importance": 5.0,
        "source_url": "https://simonwillison.net/2026/apr/20/self-hosting/",
        "is_kol_voice": True,
    },
]


class TestRenderSubject(unittest.TestCase):
    def test_default_template(self):
        s = render_subject("MorningAI {date} · {n} updates", "2026-04-20", 8, "en")
        self.assertEqual(s, "MorningAI 2026-04-20 · 8 updates")

    def test_chinese_template(self):
        s = render_subject("MorningAI 早报 {date}（{n} 条）", "2026-04-20", 8, "zh")
        self.assertEqual(s, "MorningAI 早报 2026-04-20（8 条）")

    def test_empty_template_falls_back(self):
        s = render_subject("", "2026-04-20", 8, "en")
        self.assertIn("MorningAI 2026-04-20", s)

    def test_bad_template_falls_back(self):
        s = render_subject("MorningAI {undefined_key}", "2026-04-20", 8, "en")
        self.assertIn("MorningAI 2026-04-20", s)


class TestRenderText(unittest.TestCase):
    def test_basic_structure(self):
        out = render_text(SAMPLE_ITEMS, "2026-04-20", "en")
        self.assertIn("MorningAI 2026-04-20", out)
        self.assertIn("3 notable updates today", out)
        self.assertIn("🔥", out)   # score 9.2
        self.assertIn("⭐", out)   # score 7.5
        self.assertIn("🔷", out)   # score 5.5
        self.assertIn("Anthropic Claude 4.5 Sonnet released", out)
        self.assertIn("🔗 https://anthropic.com/news/claude-4-5", out)
        self.assertIn("Powered by MorningAI", out)

    def test_empty_items(self):
        out = render_text([], "2026-04-20", "en")
        self.assertIn("No qualifying updates today", out)

    def test_chinese(self):
        out = render_text(SAMPLE_ITEMS, "2026-04-20", "zh")
        self.assertIn("共 3 条重要更新", out)
        self.assertIn("完整报告", out)

    def test_japanese(self):
        out = render_text(SAMPLE_ITEMS, "2026-04-20", "ja")
        self.assertIn("本日の注目 3 件", out)

    def test_invalid_lang_falls_back_to_en(self):
        out = render_text(SAMPLE_ITEMS, "2026-04-20", "xx")
        self.assertIn("notable updates today", out)

    def test_unsubscribe_footer(self):
        out = render_text(
            SAMPLE_ITEMS, "2026-04-20", "en",
            unsubscribe="mailto:admin@example.com?subject=Unsubscribe",
        )
        self.assertIn("admin@example.com", out)
        self.assertIn("To unsubscribe", out)


class TestRenderHtml(unittest.TestCase):
    def test_basic_structure(self):
        out = render_html(SAMPLE_ITEMS, "2026-04-20", "en", subject="MorningAI 2026-04-20")
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("<html lang=\"en\">", out)
        self.assertIn("MorningAI", out)
        self.assertIn("Anthropic", out)
        self.assertIn("https://anthropic.com/news/claude-4-5", out)
        # Inline CSS — no external <link> or <style> blocks
        self.assertNotIn("<link rel=\"stylesheet\"", out)
        self.assertNotIn("<style>", out)

    def test_html_escaping(self):
        items = [{
            "entity": "<script>alert(1)</script>",
            "title": "Bad & ugly",
            "summary": "Has <b>html</b> & symbols",
            "importance": 8,
            "source_url": "https://x.com/path?a=1&b=2",
            "verified": True,
        }]
        out = render_html(items, "2026-04-20", "en")
        self.assertNotIn("<script>alert(1)</script>", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertIn("Bad &amp; ugly", out)
        # URL kept functional via attribute escaping
        self.assertIn("https://x.com/path?a=1&amp;b=2", out)

    def test_empty_items_shows_no_items_text(self):
        out = render_html([], "2026-04-20", "zh")
        self.assertIn("今日暂无符合条件的更新", out)

    def test_unsubscribe_link(self):
        out = render_html(
            SAMPLE_ITEMS, "2026-04-20", "en",
            unsubscribe="mailto:admin@example.com",
        )
        self.assertIn("admin@example.com", out)
        self.assertIn("href=\"mailto:admin@example.com\"", out)


class TestKolSection(unittest.TestCase):
    """KOL Voices section: rendered separately from main items, no 7+ verification gate."""

    def test_text_no_section_when_disabled(self):
        out = render_text(SAMPLE_ITEMS, "2026-04-20", "en", show_kol_section=False)
        self.assertNotIn("KOL Voices", out)
        self.assertNotIn("KOL", out)

    def test_text_section_with_items(self):
        out = render_text(
            SAMPLE_ITEMS, "2026-04-20", "en",
            kol_items=SAMPLE_KOL_ITEMS, show_kol_section=True,
        )
        self.assertIn("KOL Voices", out)
        self.assertIn("@karpathy On the future of agents", out)
        self.assertIn("Why I stopped self-hosting LLMs", out)
        self.assertIn("🎙️", out)
        # Empty-state should NOT appear when items are present
        self.assertNotIn("KOL voices were quiet", out)

    def test_text_empty_state_when_no_items(self):
        out = render_text(
            SAMPLE_ITEMS, "2026-04-20", "en",
            kol_items=[], show_kol_section=True,
        )
        self.assertIn("KOL Voices", out)
        self.assertIn("KOL voices were quiet", out)

    def test_text_empty_state_zh(self):
        out = render_text(
            SAMPLE_ITEMS, "2026-04-20", "zh",
            kol_items=[], show_kol_section=True,
        )
        self.assertIn("KOL 观点", out)
        self.assertIn("今日 KOL 安静", out)

    def test_text_empty_state_ja(self):
        out = render_text(
            SAMPLE_ITEMS, "2026-04-20", "ja",
            kol_items=[], show_kol_section=True,
        )
        self.assertIn("KOL の声", out)
        self.assertIn("KOL は静か", out)

    def test_text_kol_section_renders_even_when_main_items_empty(self):
        out = render_text(
            [], "2026-04-20", "en",
            kol_items=SAMPLE_KOL_ITEMS, show_kol_section=True,
        )
        self.assertIn("No qualifying updates today", out)
        self.assertIn("KOL Voices", out)
        self.assertIn("@karpathy", out)

    def test_html_no_section_when_disabled(self):
        out = render_html(SAMPLE_ITEMS, "2026-04-20", "en", show_kol_section=False)
        self.assertNotIn("KOL Voices", out)

    def test_html_section_with_items(self):
        out = render_html(
            SAMPLE_ITEMS, "2026-04-20", "en",
            kol_items=SAMPLE_KOL_ITEMS, show_kol_section=True,
        )
        self.assertIn("KOL Voices", out)
        self.assertIn("@karpathy On the future of agents", out)
        # KOL accent color (teal) used
        self.assertIn("#0d9488", out)
        # Microphone marker
        self.assertIn("🎙️", out)

    def test_html_empty_state(self):
        out = render_html(
            SAMPLE_ITEMS, "2026-04-20", "en",
            kol_items=[], show_kol_section=True,
        )
        self.assertIn("KOL Voices", out)
        self.assertIn("KOL voices were quiet", out)

    def test_html_empty_state_zh(self):
        out = render_html(
            SAMPLE_ITEMS, "2026-04-20", "zh",
            kol_items=[], show_kol_section=True,
        )
        self.assertIn("KOL 观点", out)
        self.assertIn("今日 KOL 安静", out)

    def test_html_kol_escaping(self):
        bad_kol = [{
            "entity": "<script>alert('xss')</script>",
            "title": "Bad & ugly",
            "summary": "Has <b>html</b> & symbols",
            "importance": 5.0,
            "source_url": "https://x.com/path?a=1&b=2",
            "is_kol_voice": True,
        }]
        out = render_html(
            SAMPLE_ITEMS, "2026-04-20", "en",
            kol_items=bad_kol, show_kol_section=True,
        )
        self.assertNotIn("<script>alert('xss')</script>", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertIn("Bad &amp; ugly", out)
        self.assertIn("https://x.com/path?a=1&amp;b=2", out)


if __name__ == "__main__":
    unittest.main()
