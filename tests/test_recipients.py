"""Tests for lib/recipients.py — recipient list loading."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.recipients import (
    Recipient,
    _is_valid_email,
    _parse_env_list,
    _parse_json_file,
    load_recipients,
)


class TestEmailValidation(unittest.TestCase):
    def test_valid_addresses(self):
        for addr in ("a@b.co", "user.name+tag@example.com", "x@y.io"):
            self.assertTrue(_is_valid_email(addr), addr)

    def test_invalid_addresses(self):
        for addr in ("", "noatsign", "@nohost", "user@", "user @host.com", "user@host"):
            self.assertFalse(_is_valid_email(addr), addr)


class TestEnvListParsing(unittest.TestCase):
    def test_simple_list(self):
        rs = _parse_env_list("a@x.com,b@y.com")
        self.assertEqual([r.email for r in rs], ["a@x.com", "b@y.com"])

    def test_strips_whitespace(self):
        rs = _parse_env_list(" a@x.com , b@y.com ")
        self.assertEqual([r.email for r in rs], ["a@x.com", "b@y.com"])

    def test_skips_invalid(self):
        rs = _parse_env_list("a@x.com,invalid,b@y.com")
        self.assertEqual([r.email for r in rs], ["a@x.com", "b@y.com"])

    def test_empty_string(self):
        self.assertEqual(_parse_env_list(""), [])


class TestJsonFileParsing(unittest.TestCase):
    def _write(self, data) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, f)
        f.close()
        return Path(f.name)

    def test_basic_entries(self):
        path = self._write([
            {"email": "a@x.com", "name": "Alice", "lang": "zh", "min_score": 7},
            {"email": "b@y.com"},
        ])
        rs = _parse_json_file(path)
        self.assertEqual(len(rs), 2)
        self.assertEqual(rs[0].name, "Alice")
        self.assertEqual(rs[0].lang, "zh")
        self.assertEqual(rs[0].min_score, 7)
        self.assertEqual(rs[1].email, "b@y.com")
        self.assertTrue(rs[1].active)

    def test_inactive_kept_in_parse(self):
        # Parser keeps inactive entries; load_recipients() filters them
        path = self._write([{"email": "a@x.com", "active": False}])
        rs = _parse_json_file(path)
        self.assertEqual(len(rs), 1)
        self.assertFalse(rs[0].active)

    def test_skips_invalid_entries(self):
        path = self._write([
            {"email": "a@x.com"},
            {"email": "not-an-email"},
            {"name": "no email field"},
            "not a dict",
        ])
        rs = _parse_json_file(path)
        self.assertEqual([r.email for r in rs], ["a@x.com"])

    def test_missing_file_returns_empty(self):
        self.assertEqual(_parse_json_file(Path("/nonexistent/path.json")), [])

    def test_malformed_json_returns_empty(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        f.write("{not json")
        f.close()
        self.assertEqual(_parse_json_file(Path(f.name)), [])

    def test_non_list_returns_empty(self):
        path = self._write({"email": "a@x.com"})  # dict, not list
        self.assertEqual(_parse_json_file(path), [])


class TestLoadRecipients(unittest.TestCase):
    def test_env_only(self):
        config = {"EMAIL_RECIPIENTS": "a@x.com,b@y.com", "EMAIL_RECIPIENTS_FILE": ""}
        rs = load_recipients(config)
        self.assertEqual([r.email for r in rs], ["a@x.com", "b@y.com"])

    def test_file_overrides_env(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump([{"email": "from_file@x.com"}], f)
        f.close()
        config = {
            "EMAIL_RECIPIENTS": "from_env@x.com",
            "EMAIL_RECIPIENTS_FILE": f.name,
        }
        rs = load_recipients(config)
        self.assertEqual([r.email for r in rs], ["from_file@x.com"])

    def test_filters_inactive(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump([
            {"email": "active@x.com"},
            {"email": "paused@x.com", "active": False},
        ], f)
        f.close()
        config = {"EMAIL_RECIPIENTS_FILE": f.name}
        rs = load_recipients(config)
        self.assertEqual([r.email for r in rs], ["active@x.com"])

    def test_dedupes_case_insensitive(self):
        config = {
            "EMAIL_RECIPIENTS": "Alice@X.com,alice@x.com,bob@y.com",
            "EMAIL_RECIPIENTS_FILE": "",
        }
        rs = load_recipients(config)
        self.assertEqual(len(rs), 2)
        self.assertEqual(rs[0].email, "Alice@X.com")  # first wins
        self.assertEqual(rs[1].email, "bob@y.com")


class TestRecipientDisplay(unittest.TestCase):
    def test_with_name(self):
        self.assertEqual(
            Recipient(email="a@x.com", name="Alice").display(),
            "Alice <a@x.com>",
        )

    def test_without_name(self):
        self.assertEqual(Recipient(email="a@x.com").display(), "a@x.com")


if __name__ == "__main__":
    unittest.main()
