#!/usr/bin/env python3
"""Validate FPO Markdown front-matter fixtures against the v0.2 JSON Schema.

This validator distinguishes top-level FPO records/messages from reusable
schema helper definitions. It also verifies the canonical semantic commit.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import sys
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "runtime/schemas/fpo_records.schema.json"
EXAMPLE_ROOT = ROOT / "examples"


def front_matter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"Unclosed front matter: {path}")
    value = yaml.safe_load(text[4:end])
    return value if isinstance(value, dict) else None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def top_level_types(schema: dict[str, Any]) -> set[str]:
    types: set[str] = set()
    for branch in schema.get("oneOf", []):
        ref = branch.get("$ref") if isinstance(branch, dict) else None
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            types.add(ref.rsplit("/", 1)[-1])
    return types


def fixture_type(data: dict[str, Any]) -> str | None:
    if data.get("schema_name") == "fpo.record":
        value = data.get("record_type")
        return str(value) if value else None
    if data.get("schema_name") in {"fpo.dispatch_packet", "fpo.capability_return"}:
        value = data.get("message_type")
        return str(value) if value else None
    return None


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    expected = top_level_types(schema)

    fixture_paths: list[Path] = []
    failures: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    records: dict[str, dict[str, Any]] = {}

    for path in sorted(EXAMPLE_ROOT.rglob("*.md")):
        data = front_matter(path)
        if not isinstance(data, dict):
            continue
        kind = fixture_type(data)
        if kind is None:
            continue
        fixture_paths.append(path)
        rel = path.relative_to(EXAMPLE_ROOT).as_posix()
        records[rel] = data
        counts[kind] = counts.get(kind, 0) + 1
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        if errors:
            failures.append({
                "path": path.relative_to(ROOT).as_posix(),
                "errors": [
                    f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
                    for e in errors
                ],
            })

    seen = set(counts)
    missing = sorted(expected - seen)
    unknown = sorted(seen - expected)
    if missing:
        failures.append({
            "path": "examples",
            "errors": [f"Missing top-level fixture type: {x}" for x in missing],
        })
    if unknown:
        failures.append({
            "path": "examples",
            "errors": [f"Unknown top-level fixture type: {x}" for x in unknown],
        })

    # Verify semantic commit digests and projection digest for each committed work.
    for rel, data in records.items():
        if data.get("schema_name") != "fpo.record" or data.get("record_type") != "commit":
            continue
        base = (EXAMPLE_ROOT / rel).parent.parent
        payload = data["payload"]
        for item in payload["record_digests"]:
            target = base / item["ref"]
            got = sha256(target) if target.exists() else None
            if got != item["sha256"]:
                failures.append({
                    "path": rel,
                    "errors": [f"record digest mismatch {item['ref']}"],
                })
        projection = base / payload["projection_ref"]
        got = sha256(projection) if projection.exists() else None
        if got != payload["projection_sha256"]:
            failures.append({
                "path": rel,
                "errors": ["projection digest mismatch"],
            })

    result = {
        "status": "PASS" if not failures else "FAIL",
        "schema": SCHEMA_PATH.relative_to(ROOT).as_posix(),
        "fixture_count": len(fixture_paths),
        "top_level_types_expected": sorted(expected),
        "fixture_types": counts,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
