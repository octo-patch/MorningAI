"""Tests for lib/x_agent.py — the X_COLLECTOR_MODE gate.

The behaviour this PR is actually about: by default, collect() must not
touch the Anthropic SDK, the network, or any subprocess at all — X coverage
is deferred to the orchestrating agent's own WebSearch tool. The SDK path
only runs when explicitly opted into via X_COLLECTOR_MODE=sdk.

These tests reload the module with a patched environment so the
module-level `X_COLLECTOR_MODE` constant (read once at import time) reflects
each test's scenario, rather than whatever was in the environment when the
test process started.
"""

import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lib.x_agent as x_agent  # noqa: E402  (import after sys.path fix, matches repo convention)


def _reload_with_mode(mode):
    """Reload lib.x_agent with X_COLLECTOR_MODE set to `mode` (or unset if None)."""
    env_patch = {"X_COLLECTOR_MODE": mode} if mode is not None else {}
    with patch.dict("os.environ", env_patch, clear=False):
        if mode is None:
            import os
            os.environ.pop("X_COLLECTOR_MODE", None)
        return importlib.reload(x_agent)


class TestDefaultModeNeverTouchesSdk(unittest.TestCase):
    def tearDown(self):
        # Always leave the module in its natural (env-unset -> "agent")
        # state for any test that runs after this one in the same process.
        _reload_with_mode(None)

    def test_default_mode_is_agent(self):
        mod = _reload_with_mode(None)
        self.assertEqual(mod.X_COLLECTOR_MODE, "agent")

    def test_explicit_agent_mode(self):
        mod = _reload_with_mode("agent")
        self.assertEqual(mod.X_COLLECTOR_MODE, "agent")

    def test_default_mode_returns_immediately_with_no_items_and_a_note_not_an_error(self):
        mod = _reload_with_mode(None)
        # If the mode gate were missing (the pre-fix behaviour), this call
        # would fall through to _HAS_ANTHROPIC / _run_subagent — patch both
        # to explode, so a regression here fails loudly instead of quietly
        # returning an empty result for the wrong reason.
        with patch.object(mod, "_run_subagent", side_effect=AssertionError(
            "SDK path must not run in default 'agent' mode"
        )):
            result = mod.collect(
                {"official": {"OpenAI": ["OpenAI"]}}, "2026-08-04", "2026-08-05", "quick",
            )
        self.assertEqual(result.items, [])
        self.assertEqual(result.errors, [])
        self.assertEqual(len(result.notes), 1)
        self.assertIn("X_COLLECTOR_MODE", result.notes[0])
        self.assertIn("agent", result.notes[0])

    def test_default_mode_never_calls_run_subagent(self):
        mod = _reload_with_mode(None)
        with patch.object(mod, "_run_subagent") as mock_run:
            mod.collect({"official": {"OpenAI": ["OpenAI"]}}, "2026-08-04", "2026-08-05", "quick")
        mock_run.assert_not_called()


class TestSdkModeOptIn(unittest.TestCase):
    def tearDown(self):
        _reload_with_mode(None)

    def test_sdk_mode_without_anthropic_installed_reports_a_clear_error(self):
        mod = _reload_with_mode("sdk")
        # In this test environment `anthropic` genuinely is not installed
        # (per the standing "never install the anthropic package" rule),
        # so _HAS_ANTHROPIC is False and the SDK path must fail soft with
        # an informative error, not crash and not silently return items.
        self.assertFalse(mod._HAS_ANTHROPIC)
        result = mod.collect({"official": {"OpenAI": ["OpenAI"]}}, "2026-08-04", "2026-08-05", "quick")
        self.assertEqual(result.items, [])
        self.assertEqual(result.notes, [])
        self.assertEqual(len(result.errors), 1)
        self.assertIn("anthropic", result.errors[0].lower())

    def test_sdk_mode_would_attempt_the_subagent_path_if_anthropic_were_present(self):
        mod = _reload_with_mode("sdk")
        with patch.object(mod, "_HAS_ANTHROPIC", True), \
             patch.object(mod, "_run_subagent", return_value="[]") as mock_run:
            result = mod.collect({"official": {"OpenAI": ["OpenAI"]}}, "2026-08-04", "2026-08-05", "quick")
        # Proves the gate is mode-based, not availability-based: the same
        # handles that no-op in "agent" mode DO reach _run_subagent once
        # X_COLLECTOR_MODE=sdk and the dependency is present.
        mock_run.assert_called()
        self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
