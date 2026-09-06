from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from release import prepare_release


class ReleaseTests(unittest.TestCase):
    def test_missing_channel_is_not_guessed(self) -> None:
        result = prepare_release({"version": "1.2.0", "artifacts": ["app.zip"]})
        self.assertEqual(result["status"], "human_request")
        self.assertIn("channel", result["request"]["question"].lower())

    def test_explicit_channel_can_be_prepared(self) -> None:
        result = prepare_release({"version": "1.2.0", "channel": "stable", "artifacts": ["app.zip"]})
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["channel"], "stable")


if __name__ == "__main__":
    unittest.main()
