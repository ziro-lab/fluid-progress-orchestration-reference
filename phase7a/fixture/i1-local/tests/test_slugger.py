import sys
import unittest

sys.path.insert(0, "src")

from slugger import build_slugs


class SluggerTests(unittest.TestCase):
    def test_preserves_order_and_duplicates(self):
        result = build_slugs([" Beta Label ", "alpha", "alpha"])
        self.assertEqual(
            result["accepted"],
            [
                {"input": "Beta Label", "slug": "beta-label"},
                {"input": "alpha", "slug": "alpha"},
                {"input": "alpha", "slug": "alpha"},
            ],
        )

    def test_rejects_bad_items_and_continues(self):
        result = build_slugs(["ok", "  ", 42, "later"])
        self.assertEqual([item["input"] for item in result["accepted"]], ["ok", "later"])
        self.assertEqual([item["index"] for item in result["rejected"]], [1, 2])
        self.assertEqual(
            result["rejected"],
            [
                {"index": 1, "reason": "empty label"},
                {"index": 2, "reason": "not a string"},
            ],
        )

    def test_normalizes_labels_and_preserves_exact_shapes(self):
        result = build_slugs(["  Hello, WORLD!!  ", "--42__Café--", "こんにちは!!!"])

        self.assertEqual(set(result), {"accepted", "rejected"})
        self.assertEqual(
            result["accepted"],
            [
                {"input": "Hello, WORLD!!", "slug": "hello-world"},
                {"input": "--42__Café--", "slug": "42-caf"},
                {"input": "こんにちは!!!", "slug": ""},
            ],
        )
        self.assertTrue(all(set(item) == {"input", "slug"} for item in result["accepted"]))
        self.assertEqual(result["rejected"], [])

    def test_is_deterministic_and_does_not_mutate_input(self):
        labels = [" Zed ", "alpha", "alpha", 7]
        original = labels.copy()

        first = build_slugs(labels)
        second = build_slugs(labels)

        self.assertEqual(first, second)
        self.assertEqual(labels, original)


if __name__ == "__main__":
    unittest.main()
