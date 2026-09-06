"""Oracle-free local Flow Mini execution adapter used as a fresh subprocess."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
FLOW_ARCHIVE = REPO.parent / "phase7-references" / "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3.zip"


def run_tests(project: Path, pattern: str) -> dict[str, object]:
    completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"], cwd=project, capture_output=True, text=True, timeout=20)
    return {"returncode": completed.returncode, "status": "PASS" if completed.returncode == 0 else "FAIL", "stdout": completed.stdout, "stderr": completed.stderr, "pattern": pattern}


def write_flow_state(project: Path, job: str, lane: str, seed: str) -> None:
    stage_root = project / ".flow-mini"
    stage_root.mkdir(parents=True, exist_ok=True)
    entry = "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3/templates/.flow-mini/EXECUTION.md"
    with zipfile.ZipFile(FLOW_ARCHIVE) as archive:
        (stage_root / "EXECUTION.md").write_bytes(archive.read(entry))
    (stage_root / "CONTRACT.md").write_text(f"# {job} {lane} Contract\n\nScope: project-local implementation only.\n", encoding="utf-8", newline="\n")
    (stage_root / "ACCEPTANCE.md").write_text("# Acceptance\n\nImplementation-local tests must pass; FPO retains final acceptance and close.\n", encoding="utf-8", newline="\n")
    (stage_root / "WORKPLAN.md").write_text(json.dumps({"job": job, "lane": lane, "seed": seed, "fpo_acceptance": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("usage: worker_adapter.py JOB LANE PROJECT SEED")
    job, lane, project_text, seed = sys.argv[1:]
    project = Path(project_text)
    write_flow_state(project, job, lane, seed)
    if lane == "labels":
        (project / "src" / "labels.py").write_text("import re\n\ndef normalize_label(value):\n    words = re.findall(r'[a-z0-9]+', value.lower())\n    return '-'.join(words)\n", encoding="utf-8", newline="\n")
        changed = ["src/labels.py"]
        pattern = "test_labels.py"
    elif lane == "versions":
        (project / "src" / "versions.py").write_text("def sort_versions(values):\n    def key(value):\n        text = value if isinstance(value, str) else value['version']\n        return tuple(int(part) for part in text.split('.'))\n    return sorted(values, key=key)\n", encoding="utf-8", newline="\n")
        changed = ["src/versions.py"]
        pattern = "test_versions.py"
    elif lane == "threshold":
        (project / "src" / "threshold.py").write_text("def parse_threshold(text):\n    if text.count('=') != 1:\n        raise ValueError('invalid threshold')\n    name, value = (part.strip() for part in text.split('='))\n    if not name or not value:\n        raise ValueError('invalid threshold')\n    return name, int(value)\n", encoding="utf-8", newline="\n")
        changed = ["src/threshold.py"]
        pattern = "test_threshold.py"
    else:
        raise SystemExit(f"unknown lane {lane}")
    validation = run_tests(project, pattern)
    print(json.dumps({"schema": "fpo.phase7c.flow-mini-return.v1", "job": job, "lane": lane, "provider": "local-flow-mini-adapter", "declared_model_policy": "gpt-5.6-luna/xhigh", "fresh_context": True, "prior_transcript": False, "prior_hidden_reasoning": False, "changed_files": changed, "status": "DONE" if validation["status"] == "PASS" else "GAP", "local_validation": validation, "next_action": "parent adoption and independent validation"}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
