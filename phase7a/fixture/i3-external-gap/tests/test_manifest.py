import sys
import unittest

sys.path.insert(0, "src")

from manifest import build_manifest


class ManifestTests(unittest.TestCase):
    def test_schema_v2_preserves_identity_track_and_artifact_order(self):
        result = build_manifest(
            {
                "name": "demo",
                "version": "2.0.0",
                "channel": "canary",
                "artifacts": ["b.tgz", "a.tgz"],
            }
        )
        self.assertEqual(
            result,
            {
                "schema_version": 2,
                "name": "demo",
                "version": "2.0.0",
                "track": "canary",
                "artifacts": ["b.tgz", "a.tgz"],
            },
        )

    def test_stable_track_is_accepted(self):
        result = build_manifest(
            {
                "name": "demo",
                "version": "2.0.0",
                "channel": "stable",
                "artifacts": [],
            }
        )
        self.assertEqual(result["track"], "stable")

    def test_unknown_track_is_rejected(self):
        with self.assertRaises(ValueError):
            build_manifest(
                {
                    "name": "demo",
                    "version": "2.0.0",
                    "channel": "preview",
                    "artifacts": [],
                }
            )

    def test_equivalent_inputs_are_deterministic(self):
        config = {
            "name": "demo",
            "version": "2.0.0",
            "channel": "stable",
            "artifacts": ["z.tgz", "a.tgz", "z.tgz"],
        }
        self.assertEqual(build_manifest(config), build_manifest(dict(config)))


if __name__ == "__main__":
    unittest.main()
