"""Tests for lib/email_sender.py — message construction, headers, SMTP dispatch.

Uses unittest.mock to stub smtplib so the tests run offline.
"""

import sys
import unittest
from email import message_from_bytes
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.email_sender import (
    SendError,
    SmtpConfig,
    _build_message,
    build_unsubscribe_headers,
    send,
)


class TestBuildMessage(unittest.TestCase):
    def test_multipart_alternative(self):
        msg = _build_message(
            from_addr="from@x.com",
            to_addr="to@y.com",
            subject="Hello",
            text_body="plain body",
            html_body="<p>html body</p>",
        )
        self.assertEqual(msg["From"], "from@x.com")
        self.assertEqual(msg["To"], "to@y.com")
        self.assertEqual(msg["Subject"], "Hello")
        self.assertTrue(msg["Date"])
        self.assertTrue(msg["Message-ID"].endswith("@morning-ai>"))
        # Multipart with two parts: text + html
        self.assertTrue(msg.is_multipart())

    def test_extra_headers(self):
        msg = _build_message(
            from_addr="from@x.com",
            to_addr="to@y.com",
            subject="Hi",
            text_body="t",
            html_body="<p>h</p>",
            extra_headers={"List-Unsubscribe": "<mailto:u@x.com>"},
        )
        self.assertEqual(msg["List-Unsubscribe"], "<mailto:u@x.com>")

    def test_reply_to(self):
        msg = _build_message(
            from_addr="f@x.com", to_addr="t@y.com", subject="s",
            text_body="t", html_body="<p>h</p>",
            reply_to="reply@x.com",
        )
        self.assertEqual(msg["Reply-To"], "reply@x.com")

    def test_attachment(self):
        import tempfile
        f = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        f.write(b"\x89PNG fake bytes")
        f.close()
        msg = _build_message(
            from_addr="f@x.com", to_addr="t@y.com", subject="s",
            text_body="t", html_body="<p>h</p>",
            attachments=[Path(f.name)],
        )
        # Round-trip through bytes to check the attachment is present
        raw = msg.as_bytes()
        parsed = message_from_bytes(raw)
        filenames = [
            part.get_filename()
            for part in parsed.walk()
            if part.get_filename()
        ]
        self.assertIn(Path(f.name).name, filenames)


class TestUnsubscribeHeaders(unittest.TestCase):
    def test_empty_returns_empty(self):
        self.assertEqual(build_unsubscribe_headers(""), {})

    def test_mailto(self):
        h = build_unsubscribe_headers("mailto:u@x.com")
        self.assertEqual(h, {"List-Unsubscribe": "<mailto:u@x.com>"})

    def test_https_adds_one_click(self):
        h = build_unsubscribe_headers("https://example.com/u")
        self.assertEqual(h["List-Unsubscribe"], "<https://example.com/u>")
        self.assertEqual(h["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click")

    def test_bare_email_treated_as_mailto(self):
        h = build_unsubscribe_headers("u@x.com")
        self.assertEqual(h["List-Unsubscribe"], "<mailto:u@x.com>")


class TestSend(unittest.TestCase):
    def _smtp_cfg(self, tls="starttls"):
        return SmtpConfig(
            host="smtp.example.com", port=587, user="u", password="p",
            tls=tls, timeout=5,
        )

    @patch("lib.email_sender.smtplib.SMTP")
    def test_starttls_flow(self, mock_smtp_cls):
        mock_client = MagicMock()
        mock_smtp_cls.return_value = mock_client

        result = send(
            smtp_config=self._smtp_cfg("starttls"),
            from_addr="f@x.com", to_addr="t@y.com", subject="s",
            text_body="t", html_body="<p>h</p>",
        )

        mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=5)
        mock_client.starttls.assert_called_once()
        mock_client.login.assert_called_once_with("u", "p")
        mock_client.send_message.assert_called_once()
        mock_client.quit.assert_called_once()
        self.assertEqual(result.status, "sent")
        self.assertEqual(result.recipient, "t@y.com")
        self.assertTrue(result.message_id)

    @patch("lib.email_sender.smtplib.SMTP_SSL")
    def test_ssl_flow(self, mock_ssl_cls):
        mock_client = MagicMock()
        mock_ssl_cls.return_value = mock_client

        send(
            smtp_config=self._smtp_cfg("ssl"),
            from_addr="f@x.com", to_addr="t@y.com", subject="s",
            text_body="t", html_body="<p>h</p>",
        )

        mock_ssl_cls.assert_called_once()
        mock_client.starttls.assert_not_called()
        mock_client.login.assert_called_once_with("u", "p")
        mock_client.send_message.assert_called_once()

    @patch("lib.email_sender.smtplib.SMTP")
    def test_send_failure_raises_send_error(self, mock_smtp_cls):
        import smtplib
        mock_client = MagicMock()
        mock_client.send_message.side_effect = smtplib.SMTPRecipientsRefused({})
        mock_smtp_cls.return_value = mock_client

        with self.assertRaises(SendError) as ctx:
            send(
                smtp_config=self._smtp_cfg(),
                from_addr="f@x.com", to_addr="t@y.com", subject="s",
                text_body="t", html_body="<p>h</p>",
            )
        self.assertEqual(ctx.exception.recipient, "t@y.com")
        # Client.quit() still called even on failure
        mock_client.quit.assert_called()

    @patch("lib.email_sender.smtplib.SMTP")
    def test_connection_failure_raises_send_error(self, mock_smtp_cls):
        mock_smtp_cls.side_effect = OSError("connection refused")

        with self.assertRaises(SendError) as ctx:
            send(
                smtp_config=self._smtp_cfg(),
                from_addr="f@x.com", to_addr="t@y.com", subject="s",
                text_body="t", html_body="<p>h</p>",
            )
        self.assertIn("connection error", ctx.exception.reason)


if __name__ == "__main__":
    unittest.main()
