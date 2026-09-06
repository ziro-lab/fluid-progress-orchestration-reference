"""Verified entrypoint for reproducing the historical Phase 7C trial.

This wrapper does not change Phase 7C semantics or evidence. It fails closed on
the exact external Flow Mini archive dependency before actions that actually
need it, then preserves the Current proof-scope clarification in the
human-readable report.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
FLOW_ARCHIVE = REPO.parent / "phase7-references" / "Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3.zip"
EXPECTED_SHA256 = "454f835efac1f09d774ccc3a4bce76352761f208a6dffba9305b646f2d18f93c"
SCOPE_MARKER = "## Current proof-scope clarification"
SCOPE_NOTE = (
    "\n## Current proof-scope clarification\n\n"
    "This PASS covers the recorded deterministic local Flow Mini adapter / Phase 7B Provider integration scope. "
    "It does not by itself prove Current Flow Mini r3 Core Activation, REPLAN generation stale-result rejection, "
    "the Current Codex Plugin launcher path, or live Same-Sol Host worker isolation / stop / release behavior. "
    "See `phase7c/PROOF_SCOPE.md` and `CURRENT_FLOW_MINI_COMPOSITION.md`.\n"
)
ARCHIVE_ACTIONS = {"run", "worker"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preflight() -> None:
    if not FLOW_ARCHIVE.is_file():
        raise SystemExit(
            "Phase 7C reproduction dependency missing:\n"
            f"  expected: {FLOW_ARCHIVE}\n"
            f"  sha256:   {EXPECTED_SHA256}\n"
            "Place the exact historical Flow Mini r3 archive there; do not substitute another revision."
        )

    actual = sha256(FLOW_ARCHIVE)
    if actual != EXPECTED_SHA256:
        raise SystemExit(
            "Phase 7C Flow Mini archive hash mismatch:\n"
            f"  path:     {FLOW_ARCHIVE}\n"
            f"  expected: {EXPECTED_SHA256}\n"
            f"  actual:   {actual}\n"
            "Stop rather than guessing or silently replacing the bound revision."
        )


def preserve_scope_note() -> None:
    report = ROOT / "report.md"
    if not report.is_file():
        return
    current = report.read_text(encoding="utf-8")
    if SCOPE_MARKER in current:
        return
    report.write_text(current.rstrip() + "\n" + SCOPE_NOTE, encoding="utf-8", newline="\n")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: run_verified.py prepare|run|regression|report|worker ...")

    action = sys.argv[1]
    if action in ARCHIVE_ACTIONS:
        preflight()

    completed = subprocess.run(
        [sys.executable, str(ROOT / "run_phase7c.py"), *sys.argv[1:]],
        cwd=REPO,
    )
    if completed.returncode == 0 and action in {"run", "report"}:
        preserve_scope_note()
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
