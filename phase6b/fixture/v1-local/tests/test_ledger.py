from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ledger import summarize


class LedgerTests(unittest.TestCase):
    def test_preserves_input_order_and_exact_total(self) -> None:
        result = summarize([
            {"id": "b", "amount": "0.10"},
            {"id": "a", "amount": "0.20"},
        ])
        self.assertEqual([item["id"] for item in result["accepted"]], ["b", "a"])
        self.assertEqual(result["total"], "0.30")

    def test_rejects_bad_records_without_abort(self) -> None:
        result = summarize([
            {"id": "ok", "amount": "1.00"},
            {"id": "bad", "amount": "-2.00"},
            {"id": "later", "amount": "0.50"},
        ])
        self.assertEqual([item["id"] for item in result["accepted"]], ["ok", "later"])
        self.assertEqual([item["id"] for item in result["rejected"]], ["bad"])


if __name__ == "__main__":
    unittest.main()
