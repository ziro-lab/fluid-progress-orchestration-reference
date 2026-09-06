#!/usr/bin/env python3
"""Rebuild the canonical W-EXAMPLE semantic commit digests deterministically."""
from __future__ import annotations
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "examples/canonical_work/W-EXAMPLE"
COMMIT = WORK / "commits/COM-0001.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_front(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    return json.loads(text[4:end]), text[end + 5:].strip()


def write_front(path: Path, data: dict, body: str) -> None:
    path.write_text(
        "---\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n---\n\n" + body + "\n",
        encoding="utf-8",
    )


def main() -> None:
    data, body = read_front(COMMIT)
    adopted = sorted(
        p
        for folder in ("global", "records", "packets", "projections", "observations")
        for p in (WORK / folder).rglob("*")
        if p.is_file()
    )
    entries = [
        {"ref": p.relative_to(WORK).as_posix(), "sha256": sha256(p)}
        for p in adopted
    ]
    projection_ref = data["payload"]["projection_ref"]
    projection = WORK / projection_ref
    data["payload"]["record_digests"] = entries
    data["payload"]["projection_sha256"] = sha256(projection)
    write_front(COMMIT, data, body)
    print(f"updated {COMMIT}: {len(entries)} digests")


if __name__ == "__main__":
    main()
