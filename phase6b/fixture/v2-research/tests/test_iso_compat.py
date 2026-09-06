from __future__ import annotations

import sys
import unittest
from datetime import timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from iso_compat import parse_timestamp


class IsoCompatibilityTests(unittest.TestCase):
    def test_utc_z_is_supported_on_both_profiles(self) -> None:
        for profile in [(3, 10), (3, 11)]:
            value = parse_timestamp("2024-01-02T03:04:05Z", profile)
            self.assertEqual(value.tzinfo, timezone.utc)

    def test_offsets_remain_aware(self) -> None:
        value = parse_timestamp("2024-01-02T03:04:05+09:00", (3, 10))
        self.assertIsNotNone(value.utcoffset())

    def test_invalid_timestamp_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_timestamp("not-a-timestamp", (3, 10))

    def test_naive_timestamp_is_rejected_without_a_timezone_guess(self) -> None:
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02T03:04:05", (3, 11))

    def test_unsupported_runtime_profile_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02T03:04:05Z", (3, 12))


if __name__ == "__main__":
    unittest.main()
