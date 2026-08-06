"""Tests for lib/github.py — gh-CLI-first auth resolution, no token handling.

Uses unittest.mock to stub subprocess/http so the tests run offline and never
touch the real GitHub API or the real `gh` binary.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import github
from lib.env import get_available_sources


class TestGhCliDetection(unittest.TestCase):
    def setUp(self):
        # _GH_CLI_READY is a module-level cache — reset it before/after every
        # test so one test's monkeypatch can't leak into the next.
        github._GH_CLI_READY = None

    def tearDown(self):
        github._GH_CLI_READY = None

    @patch("lib.github.shutil.which", return_value=None)
    def test_not_ready_when_gh_missing(self, mock_which):
        self.assertFalse(github._gh_cli_ready())

    @patch("lib.github.subprocess.run")
    @patch("lib.github.shutil.which", return_value="/usr/bin/gh")
    def test_not_ready_when_gh_unauthenticated(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(github._gh_cli_ready())

    @patch("lib.github.subprocess.run")
    @patch("lib.github.shutil.which", return_value="/usr/bin/gh")
    def test_ready_when_gh_authenticated(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(github._gh_cli_ready())

    @patch("lib.github.subprocess.run")
    @patch("lib.github.shutil.which", return_value="/usr/bin/gh")
    def test_result_is_cached_across_calls(self, mock_which, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        github._gh_cli_ready()
        github._gh_cli_ready()
        github._gh_cli_ready()
        # Only ONE `gh auth status` subprocess for three calls — this is
        # what makes a multi-repo collect() run cheap.
        self.assertEqual(mock_run.call_count, 1)


class TestGhApiJson(unittest.TestCase):
    def setUp(self):
        github._GH_CLI_READY = None

    def tearDown(self):
        github._GH_CLI_READY = None

    @patch("lib.github.subprocess.run")
    def test_parses_json_stdout(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"items": []}', stderr="")
        result = github._gh_api_json("search/repositories?q=org:openai")
        self.assertEqual(result, {"items": []})
        # Never builds an Authorization header or passes a token anywhere —
        # the whole call is just `gh api <path>`.
        called_args = mock_run.call_args[0][0]
        self.assertEqual(called_args, ["gh", "api", "search/repositories?q=org:openai"])

    @patch("lib.github.subprocess.run")
    def test_returns_none_on_nonzero_exit(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        self.assertIsNone(github._gh_api_json("repos/x/y/releases"))

    @patch("lib.github.subprocess.run")
    def test_returns_none_on_bad_json(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="not json", stderr="")
        self.assertIsNone(github._gh_api_json("repos/x/y/releases"))

    @patch("lib.github.subprocess.run", side_effect=OSError("gh not found"))
    def test_returns_none_when_subprocess_fails_to_start(self, mock_run):
        self.assertIsNone(github._gh_api_json("repos/x/y/releases"))


class TestGetRepoReleases(unittest.TestCase):
    """The behavioural regression this PR is actually about: NO token is
    ever read, held, or passed — by either the gh-CLI path or the
    unauthenticated-HTTP fallback path."""

    def setUp(self):
        github._GH_CLI_READY = None

    def tearDown(self):
        github._GH_CLI_READY = None

    @patch("lib.github._gh_api_json")
    @patch("lib.github._gh_cli_ready", return_value=True)
    def test_uses_gh_api_when_gh_ready(self, mock_ready, mock_gh_api):
        mock_gh_api.return_value = [{
            "tag_name": "v1.0.0", "name": "v1.0.0", "body": "notes",
            "html_url": "https://github.com/x/y/releases/tag/v1.0.0",
            "published_at": "2026-08-05T00:00:00Z", "prerelease": False,
        }]
        releases = github.get_repo_releases("x/y", "2026-08-01", "2026-08-06")
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]["tag"], "v1.0.0")
        mock_gh_api.assert_called_once_with("repos/x/y/releases?per_page=10")

    @patch("lib.github.http.get")
    @patch("lib.github._gh_cli_ready", return_value=False)
    def test_falls_back_to_unauthenticated_http_when_gh_not_ready(self, mock_ready, mock_http_get):
        mock_http_get.return_value = [{
            "tag_name": "v2.0.0", "name": "v2.0.0", "body": "notes",
            "html_url": "https://github.com/x/y/releases/tag/v2.0.0",
            "published_at": "2026-08-05T00:00:00Z", "prerelease": False,
        }]
        releases = github.get_repo_releases("x/y", "2026-08-01", "2026-08-06")
        self.assertEqual(len(releases), 1)
        self.assertEqual(releases[0]["tag"], "v2.0.0")
        # No headers argument at all — in particular, no Authorization
        # header can leak because none is ever constructed.
        mock_http_get.assert_called_once()
        _, kwargs = mock_http_get.call_args
        self.assertNotIn("headers", kwargs)

    def test_signature_takes_no_token_argument(self):
        # A regression guard for the API shape itself: passing a `token`
        # positional/keyword argument must be a TypeError, not silently
        # accepted and ignored — that would hide a caller still trying to
        # forward a credential this module no longer wants.
        with self.assertRaises(TypeError):
            github.get_repo_releases("x/y", "2026-08-01", "2026-08-06", token="ghp_should_not_exist")  # type: ignore[call-arg]


class TestCollectHasNoTokenParam(unittest.TestCase):
    def test_collect_signature_takes_no_token_argument(self):
        with self.assertRaises(TypeError):
            github.collect({}, "2026-08-01", "2026-08-06", token="ghp_should_not_exist")  # type: ignore[call-arg]


class TestGithubAlwaysAvailable(unittest.TestCase):
    def test_github_marked_available_without_any_key(self):
        # Before this fix, "github" was gated on a configured GITHUB_TOKEN;
        # collection actually worked unauthenticated regardless, so the
        # status flag was misleading. It must now be True unconditionally,
        # matching the other keyless sources.
        available = get_available_sources({})
        self.assertTrue(available["github"])


if __name__ == "__main__":
    unittest.main()
