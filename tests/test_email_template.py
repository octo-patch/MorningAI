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


if __name__ == "__main__":
    unittest.main()
