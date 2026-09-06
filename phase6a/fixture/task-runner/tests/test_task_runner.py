from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "src" / "task_runner.py"


def invoke(payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        input_path = temp / "input.json"
        output_path = temp / "output.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(SCRIPT), str(input_path), str(output_path)], cwd=PROJECT, capture_output=True, text=True)
        return completed.returncode, json.loads(output_path.read_text(encoding="utf-8"))


class TaskRunnerTests(unittest.TestCase):
    def test_success_failure_and_order(self) -> None:
        code, report = invoke({"tasks": [
            {"id": "ok", "command": [sys.executable, "-c", "print('ok')"]},
            {"id": "bad", "command": [sys.executable, "-c", "import sys; print('bad'); sys.exit(3)"]},
        ]})
        self.assertEqual(code, 0)
        self.assertEqual([item["id"] for item in report["results"]], ["ok", "bad"])
        self.assertEqual(report["results"][0]["status"], "success")
        self.assertEqual(report["results"][1]["status"], "failed")
        self.assertEqual(report["results"][1]["exit_code"], 3)

    def test_timeout_is_reported_without_fake_success(self) -> None:
        code, report = invoke({"tasks": [{
            "id": "slow",
            "command": [sys.executable, "-c", "import time; print('before', flush=True); time.sleep(0.3)"],
            "timeout_seconds": 0.05,
        }]})
        self.assertEqual(code, 0)
        result = report["results"][0]
        self.assertEqual(result["status"], "timed_out")
        self.assertIsNone(result["exit_code"])
        self.assertIn("before", result["stdout"])

    def test_invalid_task_does_not_abort_report(self) -> None:
        code, report = invoke({"tasks": [{"id": "bad-shape", "command": "not-an-argv"}, {"id": "ok", "command": [sys.executable, "-c", "print('ok')"]}]})
        self.assertEqual(code, 0)
        self.assertEqual([item["status"] for item in report["results"]], ["invalid", "success"])


if __name__ == "__main__":
    unittest.main()
