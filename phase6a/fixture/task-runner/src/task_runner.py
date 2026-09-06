"""Initial, intentionally incomplete implementation for the Phase 6A fixture."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path


def _text_output(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def run_task(task: object) -> dict[str, object]:
    if not isinstance(task, dict):
        return {"id": None, "status": "invalid", "stdout": "", "stderr": "", "exit_code": None}

    task_id = task.get("id")
    command = task.get("command")
    has_timeout = "timeout_seconds" in task
    timeout_seconds = task.get("timeout_seconds")
    valid_timeout = not has_timeout
    if has_timeout and isinstance(timeout_seconds, (int, float)) and not isinstance(timeout_seconds, bool):
        valid_timeout = not isinstance(timeout_seconds, float) or math.isfinite(timeout_seconds)
        valid_timeout = valid_timeout and timeout_seconds > 0
    if (
        not isinstance(task_id, str)
        or not task_id
        or not isinstance(command, list)
        or not command
        or not command[0]
        or not all(isinstance(item, str) for item in command)
        or not valid_timeout
    ):
        return {"id": task_id if isinstance(task_id, str) else None, "status": "invalid", "stdout": "", "stderr": "", "exit_code": None}

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = getattr(exc, "stdout", None)
        if stdout is None:
            stdout = getattr(exc, "output", None)
        return {
            "id": task_id,
            "status": "timed_out",
            "stdout": _text_output(stdout),
            "stderr": _text_output(getattr(exc, "stderr", None)),
            "exit_code": None,
        }

    status = "success" if completed.returncode == 0 else "failed"
    return {
        "id": task_id,
        "status": status,
        "stdout": _text_output(completed.stdout),
        "stderr": _text_output(completed.stderr),
        "exit_code": completed.returncode,
    }


def build_report(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        return {"results": [], "error": "input.tasks must be an array"}
    return {"results": [run_task(task) for task in payload["tasks"]]}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: task_runner.py INPUT.json OUTPUT.json", file=sys.stderr)
        return 2
    input_path, output_path = map(Path, argv[1:])
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    report = build_report(payload)
    output_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
