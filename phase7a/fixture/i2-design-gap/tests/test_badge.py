import sys
import unittest

sys.path.insert(0, "src")

from badge import render_badge


class BadgeTests(unittest.TestCase):
    def test_resolved_stable_badge(self):
        self.assertEqual(render_badge("stable", "1.2.3"), {"text": "stable 1.2.3", "color": "green"})

    def test_resolved_canary_badge(self):
        self.assertEqual(render_badge("canary", "1.2.3"), {"text": "canary 1.2.3", "color": "amber"})


if __name__ == "__main__":
    unittest.main()
