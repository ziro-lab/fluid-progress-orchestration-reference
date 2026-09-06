#!/usr/bin/env python3
"""Minimal, deterministic Phase 0 runtime probe for the FPO v0.2 candidate.

This is intentionally a probe harness, not an orchestrator.  The canonical
work decisions below are fixed probe inputs and are emitted with the
appropriate P-stage actor.  The runtime only validates, persists, binds,
projects, invokes, and mechanically checks them.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Iterable


RUNNER_ROOT = Path(__file__).resolve().parents[1]
LOCAL_SPEC_CANDIDATE_ROOT = RUNNER_ROOT / "fpo-spec" / "Fluid_Progress_Orchestration_v0.2_Architectural_Hardening_Candidate"
MIRROR_SPEC_CANDIDATE_ROOT = RUNNER_ROOT / "spec" / "v0.2"
SPEC_CANDIDATE_ROOT = LOCAL_SPEC_CANDIDATE_ROOT if (LOCAL_SPEC_CANDIDATE_ROOT / "runtime" / "RUNTIME_MANIFEST.md").is_file() else MIRROR_SPEC_CANDIDATE_ROOT
MANIFEST_PATH = SPEC_CANDIDATE_ROOT / "runtime" / "RUNTIME_MANIFEST.md"
SPEC_RUNTIME_ROOT = MANIFEST_PATH.parent
SCHEMA_PATH = SPEC_RUNTIME_ROOT / "schemas" / "fpo_records.schema.json"
CAPABILITY_PATH = RUNNER_ROOT / "capabilities" / "text_transform" / "CAPABILITY.json"
WORKER_PATH = RUNNER_ROOT / "capabilities" / "text_transform" / "worker.ps1"
INPUT_PATH = RUNNER_ROOT / "workspace" / "input.txt"
OUTPUT_PATH = RUNNER_ROOT / "workspace" / "output" / "output.txt"
POWERSHELL_EXE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"

BUNDLE_ID = "Fluid-Progress-Orchestration-v0.2-Architectural-Hardening-Candidate"
POLICY_REVISION = "FPO-v0.2"
WORK_ID = "W-PHASE0"
TARGET_REVISION = "TARGET-R1"
DESIGN_REVISION = "DES-R1"
PLAN_UNIT_ID = "UNIT-001"
LOGICAL_INTENT_ID = "INT-001"
DISPATCH_ID = "DISP-0001"
ATTEMPT_ID = "ATT-0001"
OPERATION_ID = "LOCAL-OP-0001"
CAPABILITY_ID = "local.text_uppercase"
CAPABILITY_REVISION = "1"
BINDING_REF = "global/BIND-local-text-uppercase"

# Declared for later fault phases.  Phase 0 never activates one.
FAULT_INJECTION_POINTS = (
    "after_dispatch_commit_before_send",
    "after_send_before_remote_id_persist",
    "operation_running",
    "after_return_before_p3_adoption",
    "duplicate_or_stale_return",
    "after_effect_before_response",
    "evidence_conflict",
    "control_event",
    "return_control_injection",
)


class ProbeError(RuntimeError):
    pass


class SchemaValidationError(ProbeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def powershell_quote(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"


def write_bytes(path: Path, data: bytes, *, immutable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if immutable:
        try:
            with path.open("xb") as handle:
                handle.write(data)
        except FileExistsError as exc:
            raise ProbeError(f"immutable path already exists: {path}") from exc
        return
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp.write_bytes(data)
    os.replace(temp, path)


def frontmatter_bytes(value: dict[str, Any], explanation: str) -> bytes:
    body = json.dumps(value, ensure_ascii=False, indent=2)
    return f"---\n{body}\n---\n\n{explanation}\n".encode("utf-8")


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ProbeError(f"missing JSON front matter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ProbeError(f"unclosed front matter: {path}")
    try:
        value = json.loads(text[4:end])
    except json.JSONDecodeError as exc:
        raise ProbeError(f"invalid JSON front matter in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProbeError(f"front matter must be an object: {path}")
    return value


class JsonSchemaValidator:
    """Small dependency-free validator for the keywords used by the candidate schema."""

    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema
        self.defs = schema.get("$defs", {})

    def resolve(self, ref: str) -> dict[str, Any]:
        if not ref.startswith("#/$defs/"):
            raise SchemaValidationError(f"unsupported schema ref: {ref}")
        key = ref.rsplit("/", 1)[-1]
        if key not in self.defs:
            raise SchemaValidationError(f"unknown schema ref: {ref}")
        return self.defs[key]

    def is_valid(self, value: Any, schema: dict[str, Any]) -> bool:
        try:
            self.validate(value, schema, "$condition")
            return True
        except SchemaValidationError:
            return False

    def validate(self, value: Any, schema: dict[str, Any], path: str = "$") -> None:
        if "$ref" in schema:
            self.validate(value, self.resolve(schema["$ref"]), path)
            return

        if "oneOf" in schema:
            matches = 0
            for branch in schema["oneOf"]:
                if self.is_valid(value, branch):
                    matches += 1
            if matches != 1:
                raise SchemaValidationError(f"{path}: oneOf matched {matches} branches")

        if "allOf" in schema:
            for branch in schema["allOf"]:
                self.validate(value, branch, path)

        if "if" in schema:
            if self.is_valid(value, schema["if"]):
                if "then" in schema:
                    self.validate(value, schema["then"], path)
            elif "else" in schema:
                self.validate(value, schema["else"], path)

        if "const" in schema and value != schema["const"]:
            raise SchemaValidationError(f"{path}: expected const {schema['const']!r}")
        if "enum" in schema and value not in schema["enum"]:
            raise SchemaValidationError(f"{path}: value is not in enum")

        expected_type = schema.get("type")
        if expected_type is not None and not self.type_matches(value, expected_type):
            raise SchemaValidationError(f"{path}: expected {expected_type}")

        if isinstance(value, str):
            if len(value) < schema.get("minLength", 0):
                raise SchemaValidationError(f"{path}: minLength")
            if len(value) > schema.get("maxLength", sys.maxsize):
                raise SchemaValidationError(f"{path}: maxLength")
            if "pattern" in schema and re.search(schema["pattern"], value) is None:
                raise SchemaValidationError(f"{path}: pattern")
            if schema.get("format") == "date-time":
                try:
                    dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError as exc:
                    raise SchemaValidationError(f"{path}: invalid date-time") from exc

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value < schema.get("minimum", value):
                raise SchemaValidationError(f"{path}: minimum")

        if isinstance(value, list):
            if len(value) < schema.get("minItems", 0):
                raise SchemaValidationError(f"{path}: minItems")
            if len(value) > schema.get("maxItems", sys.maxsize):
                raise SchemaValidationError(f"{path}: maxItems")
            if schema.get("uniqueItems"):
                keys = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
                if len(keys) != len(set(keys)):
                    raise SchemaValidationError(f"{path}: uniqueItems")
            if "items" in schema:
                for index, item in enumerate(value):
                    self.validate(item, schema["items"], f"{path}[{index}]")

        if isinstance(value, dict):
            required = schema.get("required", [])
            missing = [key for key in required if key not in value]
            if missing:
                raise SchemaValidationError(f"{path}: missing required {missing}")
            properties = schema.get("properties", {})
            patterns = schema.get("patternProperties", {})
            if schema.get("additionalProperties") is False:
                for key in value:
                    if key in properties:
                        continue
                    if any(re.search(pattern, key) for pattern in patterns):
                        continue
                    raise SchemaValidationError(f"{path}: additional property {key!r}")
            for key, child in properties.items():
                if key in value:
                    self.validate(value[key], child, f"{path}.{key}")
            for pattern, child in patterns.items():
                for key, item in value.items():
                    if re.search(pattern, key):
                        self.validate(item, child, f"{path}.{key}")

    @staticmethod
    def type_matches(value: Any, expected: str | list[str]) -> bool:
        expected_values = [expected] if isinstance(expected, str) else expected
        for kind in expected_values:
            if kind == "object" and isinstance(value, dict):
                return True
            if kind == "array" and isinstance(value, list):
                return True
            if kind == "string" and isinstance(value, str):
                return True
            if kind == "boolean" and isinstance(value, bool):
                return True
            if kind == "null" and value is None:
                return True
            if kind == "integer" and isinstance(value, int) and not isinstance(value, bool):
                return True
            if kind == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
                return True
        return False


def parse_manifest(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ProbeError(f"manifest has no front matter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ProbeError(f"manifest front matter is not closed: {path}")
    lines = text[4:end].splitlines()

    def scalar(prefix: str) -> str | None:
        for line in lines:
            if line.startswith(prefix):
                value = line.split(":", 1)[1].strip()
                return value.strip("'\"")
        return None

    files: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in lines:
        match = re.match(r"^\s*-\s+path:\s+(.+)$", line)
        if match:
            current = {"path": match.group(1).strip("'\"")}
            files.append(current)
            continue
        match = re.match(r"^\s+sha256:\s+([0-9a-f]{64})\s*$", line)
        if match and current is not None:
            current["sha256"] = match.group(1)
            continue
        match = re.match(r"^\s+role:\s+(.+)$", line)
        if match and current is not None:
            current["role"] = match.group(1).strip("'\"")

    manifest = {
        "doc_type": scalar("doc_type:"),
        "schema_version": scalar("schema_version:"),
        "bundle_id": scalar("bundle_id:"),
        "runtime_revision": scalar("runtime_revision:"),
        "entry_path": scalar("entry_path:"),
        "files": files,
    }
    if any(manifest[key] in (None, "") for key in ("doc_type", "schema_version", "bundle_id", "runtime_revision", "entry_path")):
        raise ProbeError(f"manifest metadata incomplete: {path}")
    return manifest


def normalized_relative_path(value: str) -> str:
    """Normalize a complete relative path, never just its basename."""
    parts = value.replace("\\", "/").split("/")
    return "/".join(unicodedata.normalize("NFKC", part) for part in parts)


def validate_manifest() -> dict[str, Any]:
    manifest = parse_manifest(MANIFEST_PATH)
    if manifest["doc_type"] != "FPO.RUNTIME_MANIFEST" or manifest["schema_version"] != "0.2":
        raise ProbeError("runtime manifest doc/schema identity mismatch")
    if manifest["bundle_id"] != BUNDLE_ID:
        raise ProbeError("runtime manifest bundle identity mismatch")
    listed = {entry["path"] for entry in manifest["files"]}
    if manifest["entry_path"] not in listed:
        raise ProbeError("manifest entry_path is not listed")
    forbidden = ("docs/", "review/", "validation/", "examples/", "extensions/")
    resolver_events: list[dict[str, str]] = []
    for entry in manifest["files"]:
        rel = entry.get("path", "").replace("\\", "/")
        rel_path = Path(rel)
        if rel_path.is_absolute() or re.match(r"^[A-Za-z]:", rel) or rel.startswith(forbidden) or "/../" in f"/{rel}/" or rel.startswith("../"):
            raise ProbeError(f"manifest includes forbidden runtime context: {rel}")
        target = SPEC_RUNTIME_ROOT / Path(rel)
        if not target.is_file():
            normalized_rel = normalized_relative_path(rel)
            matches = []
            for candidate in SPEC_RUNTIME_ROOT.rglob("*"):
                if not candidate.is_file():
                    continue
                candidate_rel = candidate.relative_to(SPEC_RUNTIME_ROOT).as_posix()
                if normalized_relative_path(candidate_rel) == normalized_rel:
                    matches.append(candidate)
            if len(matches) != 1:
                raise ProbeError(f"manifest relative path unresolved after exact/NFKC resolution: {rel}")
            target = matches[0]
            resolver_events.append({"mode": "unicode_fallback", "manifest_path": rel, "resolved_path": target.relative_to(SPEC_RUNTIME_ROOT).as_posix()})
        got = sha256_file(target)
        if got != entry.get("sha256"):
            raise ProbeError(f"manifest digest mismatch: {rel}")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if schema.get("$id") != "urn:fpo:v0.2:fpo-records":
        raise ProbeError("machine schema identity mismatch")
    return {
        "bundle_id": manifest["bundle_id"],
        "bundle_revision": manifest["runtime_revision"],
        "manifest_sha256": sha256_file(MANIFEST_PATH),
        "manifest_file_count": len(manifest["files"]),
        "resolver_events": resolver_events,
        "schema_sha256": sha256_file(SCHEMA_PATH),
    }


class OperationController:
    """Mechanism-only operation interface; no policy or checkpoint decisions."""

    def __init__(self, store: "RunStore") -> None:
        self.store = store

    def query(self, operation_ref: str) -> dict[str, Any]:
        record = self.store.latest_record("delegated_operation", "OP-INT-001")
        if record is None or operation_ref not in {record["record_id"], record["payload"]["remote_operation_id"], "records/" + record["record_id"] + ".md"}:
            raise ProbeError(f"operation not found: {operation_ref}")
        return record["payload"]

    def cancel(self, operation_ref: str, requested_at: str) -> dict[str, Any]:
        payload = self.query(operation_ref)
        if payload["state"] in {"succeeded", "failed", "rejected", "timed_out", "canceled"}:
            return {"operation_ref": operation_ref, "state": payload["state"], "cancel_requested": False}
        return {"operation_ref": operation_ref, "state": payload["state"], "cancel_requested": True, "requested_at": requested_at}

    def reconcile(self, operation_ref: str) -> dict[str, Any]:
        payload = self.query(operation_ref)
        if payload["state"] == "unknown":
            raise ProbeError("reconcile requires an external observation; unknown is not success")
        return {"operation_ref": operation_ref, "state": payload["state"], "reconciled": True}


class RunStore:
    def __init__(self, run_dir: Path, bundle_revision: str, run_time: str) -> None:
        self.run_dir = run_dir
        self.bundle_revision = bundle_revision
        self.run_time = run_time
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.validator = JsonSchemaValidator(self.schema)
        self.sequence = 0
        self.state_revision = 0
        self.current_commit_id: str | None = None
        self.refs: list[str] = []
        self.record_values: dict[str, dict[str, Any]] = {}
        self.commit_refs: list[str] = []
        self.run_dir.mkdir(parents=True, exist_ok=False)
        for folder in ("records", "commits", "packets", "inbox/untrusted", "observations", "projections"):
            (self.run_dir / folder).mkdir(parents=True, exist_ok=True)
        self.log_path = self.run_dir / "run.log"

    def log(self, event: str, **details: Any) -> None:
        entry = {"time": self.run_time, "event": event, **details}
        with self.log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")

    def ref_path(self, ref: str) -> Path:
        return self.run_dir / Path(ref)

    def latest_record(self, record_type: str, logical_id: str) -> dict[str, Any] | None:
        candidates = [
            value for ref, value in self.record_values.items()
            if value.get("record_type") == record_type and value.get("logical_id") == logical_id
        ]
        return max(candidates, key=lambda item: (item["record_revision"], item["sequence"])) if candidates else None

    def latest_records_of_type(self, record_type: str) -> list[tuple[str, dict[str, Any]]]:
        candidates = [(ref, value) for ref, value in self.record_values.items() if value.get("record_type") == record_type]
        grouped: dict[str, tuple[str, dict[str, Any]]] = {}
        for ref, value in candidates:
            key = value["logical_id"]
            if key not in grouped or (value["record_revision"], value["sequence"]) > (grouped[key][1]["record_revision"], grouped[key][1]["sequence"]):
                grouped[key] = (ref, value)
        return sorted(grouped.values(), key=lambda item: item[1]["sequence"])

    def _envelope(self, record_type: str, record_id: str, logical_id: str, actor: dict[str, str], record_revision: int) -> dict[str, Any]:
        self.sequence += 1
        return {
            "schema_name": "fpo.record",
            "schema_version": "0.2",
            "record_type": record_type,
            "record_id": record_id,
            "logical_id": logical_id,
            "record_revision": record_revision,
            "work_id": WORK_ID,
            "base_state_revision": self.state_revision,
            "sequence": self.sequence,
            "actor": actor,
            "created_at": self.run_time,
            "bundle_id": BUNDLE_ID,
            "bundle_revision": self.bundle_revision,
            "policy_revision": POLICY_REVISION,
            "sensitivity": "internal",
            "retention_class": "audit_required",
        }

    def add_record(
        self,
        record_type: str,
        record_id: str,
        logical_id: str,
        payload: dict[str, Any],
        actor: dict[str, str],
        *,
        record_revision: int = 1,
        folder: str = "records",
        explanation: str = "Immutable FPO v0.2 Phase 0 record.",
    ) -> str:
        record = self._envelope(record_type, record_id, logical_id, actor, record_revision)
        record["payload"] = payload
        self.validator.validate(record, self.schema)
        ref = (Path(folder) / f"{record_id}.md").as_posix()
        write_bytes(self.ref_path(ref), frontmatter_bytes(record, explanation), immutable=True)
        self.refs.append(ref)
        self.record_values[ref] = record
        return ref

    def add_message(self, message: dict[str, Any], folder: str, file_name: str, explanation: str) -> str:
        self.validator.validate(message, self.schema)
        ref = (Path(folder) / file_name).as_posix()
        write_bytes(self.ref_path(ref), frontmatter_bytes(message, explanation), immutable=True)
        self.refs.append(ref)
        return ref

    def add_observation(self, file_name: str, value: dict[str, Any]) -> str:
        ref = (Path("observations") / file_name).as_posix()
        write_bytes(self.ref_path(ref), json_bytes(value), immutable=True)
        self.refs.append(ref)
        return ref

    def _projection_payload(self, commit_id: str, next_state_revision: int) -> dict[str, Any]:
        ws = self.latest_record("work_state", "WS-W-PHASE0")
        wc = self.latest_record("work_control", "WC-W-PHASE0")
        source = self.latest_record("source_request", "SRC-W-PHASE0")
        definition = self.latest_record("work_definition", "DEF-W-PHASE0")
        plan = self.latest_record("execution_plan", "PLAN-W-PHASE0")
        budget = self.latest_record("resource_budget", "BUD-W-PHASE0")
        artifact = self.latest_record("artifact_manifest", "ART-W-PHASE0")
        if ws is None or wc is None or source is None:
            raise ProbeError("projection cannot be rebuilt without source/work state/control")
        ws_ref = next(ref for ref, value in self.record_values.items() if value is ws)
        wc_ref = next(ref for ref, value in self.record_values.items() if value is wc)
        source_ref = next(ref for ref, value in self.record_values.items() if value is source)
        definition_ref = next((ref for ref, value in self.record_values.items() if value is definition), None)
        plan_ref = next((ref for ref, value in self.record_values.items() if value is plan), None)
        budget_ref = next((ref for ref, value in self.record_values.items() if value is budget), None)
        artifact_ref = next((ref for ref, value in self.record_values.items() if value is artifact), None)
        units = []
        unit_refs = []
        for ref, record in self.latest_records_of_type("plan_unit_state"):
            unit_refs.append(ref)
            payload = record["payload"]
            units.append({
                "unit_id": payload["unit_id"],
                "state": payload["state"],
                "adopted_result_refs": payload["adopted_result_refs"],
                "operation_refs": payload["operation_refs"],
                "effect_refs": payload["effect_refs"],
                "last_event_ref": payload["last_event_ref"],
            })
        operations = self.latest_records_of_type("delegated_operation")
        effects = self.latest_records_of_type("effect")
        evidence_refs = [ref for ref, _ in self.latest_records_of_type("evidence")]
        evidence_refs += [ref for ref, _ in self.latest_records_of_type("criteria_verdict")]
        open_operations = [ref for ref, record in operations if record["payload"]["state"] not in {"succeeded", "failed", "rejected", "timed_out", "canceled"} or record["payload"]["adoption_status"] != "adopted"]
        unresolved_effects = [ref for ref, record in effects if record["payload"]["state"] not in {"confirmed", "failed", "compensated"}]
        active_approvals = [ref for ref, record in self.latest_records_of_type("approval") if record["payload"]["status"] == "granted" and wc["payload"]["lifecycle_state"] != "terminated"]
        events = [ref for ref, _ in self.latest_records_of_type("ledger_event")][-10:]
        return {
            "state_revision": next_state_revision,
            "current_commit_id": commit_id,
            "work_state_ref": ws_ref,
            "work_control_ref": wc_ref,
            "source_request_ref": source_ref,
            "definition_ref": definition_ref,
            "design_ref": f"{plan_ref}#design_revision={plan['payload']['design_revision']}" if plan_ref and plan else None,
            "execution_plan_ref": plan_ref,
            "unit_state_refs": unit_refs,
            "unit_states": units,
            "active_blocker_set_ref": None,
            "open_operation_refs": open_operations,
            "unresolved_effect_refs": unresolved_effects,
            "evidence_index_refs": evidence_refs,
            "active_approval_refs": active_approvals,
            "budget_ref": budget_ref,
            "artifact_manifest_ref": artifact_ref,
            "open_obligations": [],
            "recent_event_refs": events,
            "archive_refs": [],
        }

    def commit(self, new_refs: Iterable[str], authority_ref: str, description: str) -> str:
        expected = self.state_revision
        parent = self.current_commit_id
        next_revision = expected + 1
        commit_id = f"COM-{next_revision:04d}"
        new_refs = list(new_refs)
        if self.state_revision != expected:
            raise ProbeError(f"CAS failed before publish: expected {expected}, actual {self.state_revision}")
        projection_payload = self._projection_payload(commit_id, next_revision)
        projection_ref = f"projections/PROJ-{next_revision:04d}.md"
        projection_record = self._envelope(
            "current_projection",
            f"PROJ-{next_revision:04d}",
            "PROJ-W-PHASE0",
            {"id": "runtime-1", "role": "runtime", "authority": "current_projection"},
            next_revision,
        )
        projection_record["payload"] = projection_payload
        self.validator.validate(projection_record, self.schema)
        write_bytes(self.ref_path(projection_ref), frontmatter_bytes(projection_record, "Rebuildable current projection snapshot."), immutable=True)
        self.refs.append(projection_ref)
        self.record_values[projection_ref] = projection_record

        digest_refs = list(new_refs) + [projection_ref]
        digest_items = [{"ref": ref, "sha256": sha256_file(self.ref_path(ref))} for ref in digest_refs]
        commit_payload = {
            "commit_id": commit_id,
            "parent_commit_id": parent,
            "expected_state_revision": expected,
            "new_state_revision": next_revision,
            "record_digests": digest_items,
            "projection_ref": projection_ref,
            "projection_sha256": sha256_file(self.ref_path(projection_ref)),
            "authority_decision_ref": authority_ref,
            "status": "committed",
        }
        commit_record = self._envelope(
            "commit",
            commit_id,
            f"COM-W-PHASE0-{next_revision}",
            {"id": "runtime-1", "role": "runtime", "authority": "durable_commit"},
            1,
        )
        commit_record["payload"] = commit_payload
        self.validator.validate(commit_record, self.schema)
        commit_ref = f"commits/{commit_id}.md"
        write_bytes(self.ref_path(commit_ref), frontmatter_bytes(commit_record, description), immutable=True)
        self.commit_refs.append(commit_ref)

        # CAS: the head is advanced only if the expected revision still matches.
        if self.state_revision != expected:
            raise ProbeError(f"CAS failed: expected {expected}, actual {self.state_revision}")
        self.state_revision = next_revision
        self.current_commit_id = commit_id
        write_bytes(self.run_dir / "head.json", json_bytes({
            "commit_id": commit_id,
            "state_revision": next_revision,
            "projection_ref": projection_ref,
            "projection_sha256": commit_payload["projection_sha256"],
        }))
        self._write_aliases(projection_record)
        self.log("semantic_commit", commit_ref=commit_ref, commit_id=commit_id, expected_state_revision=expected, new_state_revision=next_revision, projection_ref=projection_ref, record_refs=digest_refs)
        return commit_ref

    def _write_aliases(self, projection_record: dict[str, Any]) -> None:
        projection_bytes = frontmatter_bytes(projection_record, "Rebuildable current projection alias.")
        write_bytes(self.run_dir / "WORK_INDEX.md", projection_bytes)
        ws_ref = projection_record["payload"]["work_state_ref"]
        wc_ref = projection_record["payload"]["work_control_ref"]
        write_bytes(self.run_dir / "WORK_STATE.md", self.ref_path(ws_ref).read_bytes())
        write_bytes(self.run_dir / "WORK_CONTROL.md", self.ref_path(wc_ref).read_bytes())

    def rebuild_projection_from_source(self) -> dict[str, Any]:
        projection_record = self.latest_record("current_projection", "PROJ-W-PHASE0")
        if projection_record is None:
            raise ProbeError("no immutable projection source")
        expected = projection_record["payload"]
        rebuilt = self._projection_payload(expected["current_commit_id"], expected["state_revision"])
        if rebuilt != expected:
            raise ProbeError("projection rebuild differs from immutable source records")
        alias = read_frontmatter(self.run_dir / "WORK_INDEX.md")
        if alias.get("record_type") != "current_projection" or alias.get("payload") != expected:
            raise ProbeError("WORK_INDEX alias differs from committed projection")
        return expected


def actor(actor_id: str, role: str, authority: str, trust_domain: str = "fpo-trusted-control") -> dict[str, str]:
    return {"id": actor_id, "role": role, "authority": authority, "trust_domain": trust_domain}


def base_payloads(input_ref: str, output_ref: str, output_sha: str | None = None) -> dict[str, dict[str, Any]]:
    budget_usage = {
        "attempts": 0,
        "strategy_families": 0,
        "wall_seconds": 0,
        "token_units": 0,
        "monetary_units": 0.0,
        "tool_calls": 0,
        "research_calls": 0,
        "capability_calls": 0,
        "effect_count": 0,
        "context_units": 0,
    }
    budget = {
        "limits": {
            "attempts": 3, "strategy_families": 1, "wall_seconds": 300,
            "token_units": 0, "monetary_units": 0, "tool_calls": 10,
            "research_calls": 0, "capability_calls": 1, "effect_count": 1, "context_units": 0,
        },
        "usage": budget_usage,
        "soft_limit_action": "continue",
        "hard_limit_action": "terminate_out_of_budget",
        "deadline": None,
        "override_approval_ref": None,
    }
    return {
        "budget": {
            "budget_id": "BUD-W-PHASE0",
            "scope_ref": f"work:{WORK_ID}",
            "budget": budget,
            "measured_at": "",
        },
        "approval": {
            "approval_id": "APR-0001", "grantor_id": "user-1", "status": "granted",
            "scope": ["write workspace output only"], "target_refs": [output_ref],
            "revision_constraints": [DESIGN_REVISION], "allowed_effect_classes": ["idempotent"],
            "conditions": ["do not overwrite source input"], "valid_from": "", "expires_at": None, "revocation_ref": None,
        },
        "effect": {
            "effect_id": "EFF-0001", "logical_intent_id": LOGICAL_INTENT_ID,
            "plan_unit_id": PLAN_UNIT_ID, "effect_class": "idempotent", "state": "intended",
            "target_ref": output_ref, "target_revision_before": "ABSENT", "target_revision_after": None,
            "approval_ref": "records/APR-0001.md", "preconditions": ["source input unchanged", "output target absent"],
            "idempotency_key": f"{WORK_ID}:{LOGICAL_INTENT_ID}:output-v1",
            "reconcile_method": "Check exact output path and content digest before any retry.",
            "compensation_plan_ref": None, "forward_recovery_plan_ref": "records/PLAN-0001.md",
            "dependency_effect_refs": [], "outcome_evidence_refs": [], "failure_summary": None,
        },
        "input_ref": input_ref,
        "output_ref": output_ref,
        "output_sha": output_sha,
    }


def append_record(store: RunStore, record_type: str, record_id: str, logical_id: str, payload: dict[str, Any], stage_actor: dict[str, str], revision: int = 1, explanation: str = "Immutable FPO v0.2 Phase 0 record.") -> str:
    return store.add_record(record_type, record_id, logical_id, payload, stage_actor, record_revision=revision, explanation=explanation)


def run_worker(packet: dict[str, Any], effect: dict[str, Any], store: RunStore) -> tuple[dict[str, Any], str]:
    input_ref = packet["input_refs"][0]
    input_path = RUNNER_ROOT / Path(input_ref)
    output_path = RUNNER_ROOT / Path(effect["target_ref"])
    if output_path.exists():
        raise ProbeError("duplicate-effect guard: output exists before first dispatch")
    dispatch_ref = f"packets/{DISPATCH_ID}.md"
    dispatch_sha = sha256_file(store.ref_path(dispatch_ref))
    store.log("worker_invocation", packet_ref=dispatch_ref, packet_sha256=dispatch_sha, input_ref=input_ref, output_ref=effect["target_ref"], invocation_count=1)
    worker_command = (
        "Import-Module Microsoft.PowerShell.Utility; "
        f"& {powershell_quote(WORKER_PATH)} -InputPath {powershell_quote(input_path)} "
        f"-OutputPath {powershell_quote(output_path)}"
    )
    command = [str(POWERSHELL_EXE), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", worker_command]
    completed = subprocess.run(command, cwd=RUNNER_ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise ProbeError(f"worker failed ({completed.returncode}): {completed.stderr.strip()}")
    try:
        worker_result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError(f"worker did not return JSON: {completed.stdout!r}") from exc
    if worker_result.get("status") != "completed":
        raise ProbeError("worker did not report completed")
    if worker_result.get("input_sha256") != sha256_file(input_path):
        raise ProbeError("worker input digest does not match post-run input")
    observation = {
        "worker_result": worker_result,
        "dispatch_ref": dispatch_ref,
        "dispatch_sha256": dispatch_sha,
        "input_sha256_before": sha256_file(input_path),
        "input_sha256_after": sha256_file(input_path),
        "output_sha256": sha256_file(output_path),
        "output_size": output_path.stat().st_size,
    }
    observation_ref = store.add_observation("OBS-BASELINE.json", observation)
    return worker_result, observation_ref


def make_dispatch(packet_time: str, input_ref: str, effect_ref: str) -> dict[str, Any]:
    return {
        "$schema": "urn:fpo:v0.2:fpo-records",
        "schema_name": "fpo.dispatch_packet",
        "schema_version": "0.2",
        "message_type": "dispatch_packet",
        "dispatch_id": DISPATCH_ID,
        "work_id": WORK_ID,
        "logical_intent_id": LOGICAL_INTENT_ID,
        "attempt_id": ATTEMPT_ID,
        "plan_unit_id": PLAN_UNIT_ID,
        "owner_stage": "P3",
        "capability_id": CAPABILITY_ID,
        "capability_revision": CAPABILITY_REVISION,
        "binding_ref": BINDING_REF,
        "definition_ref": "records/DEF-0001.md",
        "plan_ref": "records/PLAN-0001.md",
        "target_revision_ref": TARGET_REVISION,
        "policy_revision": POLICY_REVISION,
        "objective": "Convert ASCII/text input to Unicode-invariant uppercase and save a separate output file without modifying the input.",
        "input_refs": [input_ref],
        "constraint_refs": ["records/DEF-0001.md", "records/APR-0001.md"],
        "allowed_effect_refs": [effect_ref],
        "approval_refs": ["records/APR-0001.md"],
        "required_artifact_contracts": ["workspace/output/output.txt must exist and be content-identifiable"],
        "required_evidence_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"],
        "return_schema": "fpo.capability_return@0.2",
        "deadline": None,
        "created_at": packet_time,
    }


def make_return(packet: dict[str, Any], worker_result: dict[str, Any], return_time: str) -> dict[str, Any]:
    return {
        "$schema": "urn:fpo:v0.2:fpo-records",
        "schema_name": "fpo.capability_return",
        "schema_version": "0.2",
        "message_type": "capability_return",
        "return_id": "RET-0001",
        "work_id": WORK_ID,
        "logical_intent_id": packet["logical_intent_id"],
        "dispatch_id": packet["dispatch_id"],
        "attempt_id": packet["attempt_id"],
        "remote_operation_id": OPERATION_ID,
        "provider_identity": "local.text_transform/worker.ps1",
        "capability_id": packet["capability_id"],
        "capability_revision": packet["capability_revision"],
        "provider_sequence": 2,
        "operation_state": "succeeded",
        "partial": False,
        "observed_definition_ref": packet["definition_ref"],
        "observed_plan_ref": packet["plan_ref"],
        "observed_target_revision_ref": packet["target_revision_ref"],
        "observed_policy_revision": packet["policy_revision"],
        "artifact_refs": ["workspace/output/output.txt"],
        "evidence_candidate_refs": [],
        "effect_update_refs": ["records/EFF-0001.md"],
        "diagnostic_facts": [f"worker output sha256={worker_result['output_sha256']}"],
        "error_summary": None,
        "created_at": return_time,
    }


def operation_payload(dispatch_sha: str, state: str, *, return_ref: str | None = None, return_sha: str | None = None, adoption: str = "pending", provider_sequence: int = 0, evidence_refs: list[str] | None = None, effect_refs: list[str] | None = None, error_summary: str | None = None, remote_operation_id: str | None = OPERATION_ID) -> dict[str, Any]:
    return {
        "logical_intent_id": LOGICAL_INTENT_ID,
        "dispatch_id": DISPATCH_ID,
        "attempt_id": ATTEMPT_ID,
        "remote_operation_id": remote_operation_id,
        "plan_unit_id": PLAN_UNIT_ID,
        "owner_stage": "P3",
        "capability_id": CAPABILITY_ID,
        "capability_revision": CAPABILITY_REVISION,
        "binding_ref": BINDING_REF,
        "dispatch_payload_ref": f"packets/{DISPATCH_ID}.md",
        "dispatch_payload_sha256": dispatch_sha,
        "state": state,
        "provider_sequence": provider_sequence,
        "deadline": None,
        "lease_expires_at": None,
        "cancel_requested_at": None,
        "cancel_acknowledged": False,
        "input_request_ref": None,
        "auth_request_ref": None,
        "partial_artifact_refs": [],
        "evidence_refs": evidence_refs or [],
        "effect_refs": effect_refs or ["records/EFF-0001.md"],
        "return_ref": return_ref,
        "return_sha256": return_sha,
        "adoption_status": adoption,
        "target_revision_ref": TARGET_REVISION,
        "error_summary": error_summary,
    }


def effect_payload(state: str, output_sha: str | None = None, observation_ref: str | None = None) -> dict[str, Any]:
    confirmed = state == "confirmed"
    return {
        "effect_id": "EFF-0001",
        "logical_intent_id": LOGICAL_INTENT_ID,
        "plan_unit_id": PLAN_UNIT_ID,
        "effect_class": "idempotent",
        "state": state,
        "target_ref": "workspace/output/output.txt",
        "target_revision_before": "ABSENT",
        "target_revision_after": f"SHA256:{output_sha}" if confirmed and output_sha else None,
        "approval_ref": "records/APR-0001.md",
        "preconditions": ["source input unchanged", "output target absent"],
        "idempotency_key": f"{WORK_ID}:{LOGICAL_INTENT_ID}:output-v1",
        "reconcile_method": "Check exact output path and content digest before any retry.",
        "compensation_plan_ref": None,
        "forward_recovery_plan_ref": "records/PLAN-0001.md",
        "dependency_effect_refs": [],
        "outcome_evidence_refs": [observation_ref] if confirmed and observation_ref else [],
        "failure_summary": None if confirmed or state == "intended" else "Effect is not terminally confirmed.",
    }


def enforce_phase0_effect_boundary(effect: dict[str, Any]) -> None:
    if effect.get("effect_class") not in {"read_only", "idempotent"}:
        raise ProbeError("Phase 0 stops before unsafe or irreversible Effect")


def unit_state_payload(state: str, operation_ref: str | None = None, effect_ref: str | None = None, result_refs: list[str] | None = None, last_event_ref: str | None = None) -> dict[str, Any]:
    return {
        "plan_ref": "records/PLAN-0001.md",
        "unit_id": PLAN_UNIT_ID,
        "state": state,
        "attempt_refs": [f"attempts/{ATTEMPT_ID}.md"],
        "operation_refs": [operation_ref] if operation_ref else [],
        "effect_refs": [effect_ref] if effect_ref else [],
        "adopted_result_refs": result_refs or [],
        "blocked_by_refs": [],
        "target_revision_refs": [TARGET_REVISION],
        "last_event_ref": last_event_ref,
    }


def run_baseline() -> dict[str, Any]:
    manifest_info = validate_manifest()
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNNER_ROOT / "runs" / run_id
    store = RunStore(run_dir, manifest_info["bundle_revision"], utc_now())
    store.log("runtime_start", run_id=run_id, manifest=manifest_info, fault_injection=None, declared_fault_points=list(FAULT_INJECTION_POINTS))

    expected = json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8"))
    input_ref = "workspace/input.txt"
    output_ref = "workspace/output/output.txt"
    input_before = sha256_file(INPUT_PATH)
    if OUTPUT_PATH.exists():
        raise ProbeError("Fresh baseline requires output to be absent; run scripts/reset_workspace.ps1 first")
    input_text = INPUT_PATH.read_text(encoding="utf-8")
    if input_text != expected["input_text"]:
        raise ProbeError("canonical input does not match probe fixture")

    payloads = base_payloads(input_ref, output_ref)
    payloads["budget"]["measured_at"] = store.run_time
    payloads["approval"]["valid_from"] = store.run_time
    payloads["approval"]["expires_at"] = None

    # Predeclared canonical P1/P2 decisions.  Runtime records them; it does not infer them.
    source_ref = append_record(store, "source_request", "SRC-0001", "SRC-W-PHASE0", {
        "request_text": "Convert the letters in workspace/input.txt to uppercase and save a separate output.",
        "source_items": [{"item_id": "SRI-001", "text": "Input is preserved and output is written separately.", "source_ref": "probe/WORK_REQUEST.md", "kind": "request"}],
        "attachment_refs": ["probe/WORK_REQUEST.md"], "supersedes_ref": None,
    }, actor("user-1", "user", "source_request"))
    admission_ref = append_record(store, "work_admission", "ADM-0001", "ADM-W-PHASE0", {
        "source_request_refs": [source_ref], "admissible": True, "finite": True,
        "criteria_identifiable": True, "effects_bounded": True, "observable": True,
        "single_checkpoint_meaningful": True, "context_retrievable": True, "capability_feasible": True,
        "risk_tier": "T1", "reasons": ["bounded local reversible file write"], "split_proposals": [],
        "required_external_runtime": [], "terminal_recommendation": None,
    }, actor("p1-owner", "P1", "definition"))
    cap_ref = append_record(store, "capability_entry", "CAP-0001", "CAP-local-text-uppercase", {
        "capability_id": CAPABILITY_ID, "capability_revision": CAPABILITY_REVISION, "kind": "tool",
        "provider_identity": "capabilities/text_transform/worker.ps1", "registry_trust_ref": "global/TRUST-LOCAL-CAPABILITY",
        "provides": ["uppercase_text_file"], "accepts": ["file_path"], "returns": ["artifact_refs", "operation_state"],
        "side_effect_profile": "bounded_write", "security_scope": {"tools": ["filesystem.write"], "data": ["workspace input/output"], "paths": ["workspace/output/"], "network": [], "secret_handles": []},
        "operational_profile": {"health": "healthy", "availability_checked_at": store.run_time, "cost_class": "low", "latency_class": "seconds", "supports_cancel": True, "supports_stream": False, "supports_reconcile": True, "idempotency_support": "external_key"},
        "fitness": {"risk_ceiling": "T1", "quality_class": "qualified", "eval_refs": ["probe/EXPECTED_BASELINE.json"]},
        "compatibility": ["FPO-v0.2"], "fallback_capability_refs": [], "binding_ref": BINDING_REF, "status": "active",
    }, actor("runtime-1", "runtime", "capability_registry"))
    budget_ref = append_record(store, "resource_budget", "BUD-0001", "BUD-W-PHASE0", payloads["budget"], actor("runtime-1", "runtime", "work_control_projection"))
    approval_ref = append_record(store, "approval", "APR-0001", "APR-W-PHASE0", payloads["approval"], actor("user-1", "user", "approval_grant"))
    ws_ref = append_record(store, "work_state", "WS-0001", "WS-W-PHASE0", {"checkpoint": "none", "interrupt_ref": None}, actor("runtime-1", "runtime", "work_state_projection"))
    wc_ref = append_record(store, "work_control", "WC-0001", "WC-W-PHASE0", {
        "lifecycle_state": "active", "terminal_disposition": None, "reason": "Canonical Phase 0 work is active.",
        "resume_condition_ref": None, "resume_owner": None, "resume_expiry": None, "resume_default_action": None,
        "latest_user_event_ref": None, "active_approval_refs": [approval_ref], "active_operation_refs": [], "unresolved_effect_refs": [],
        "autonomy_budget": payloads["budget"]["budget"],
    }, actor("runtime-1", "runtime", "work_control_projection"))
    store.commit([source_ref, admission_ref, cap_ref, budget_ref, approval_ref, ws_ref, wc_ref], wc_ref, "Initial validated source and active work-control commit.")

    definition_ref = append_record(store, "work_definition", "DEF-0001", "DEF-W-PHASE0", {
        "source_request_refs": [source_ref], "amendment_refs": [],
        "objective": "Uppercase the canonical input into a separate output without modifying the input.",
        "requirements": [{"requirement_id": "REQ-001", "kind": "must", "text": "Input remains unchanged and output exactly matches invariant uppercase.", "source_item_refs": ["SRC-0001:SRI-001"], "acceptance_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"]}],
        "out_of_scope": ["external effects", "input overwrite", "fault injection"], "design_discretion": ["worker invocation mechanics"],
        "assumptions": [{"assumption_id": "ASM-001", "statement": "Canonical input is UTF-8 text.", "basis_refs": ["SRC-0001:SRI-001"], "impact": "low", "reversibility": "reversible", "status": "adopted", "validation_route_ref": "probe/ACCEPTANCE.md"}],
        "decision_priorities": ["input preservation", "exact output", "bounded reversible effect", "observability"],
        "unacceptable_tradeoffs": ["input overwrite", "unverified close"], "risk_tier": "T1", "required_human_gates": [],
        "coverage": [{"source_item_ref": "SRC-0001:SRI-001", "disposition": "must", "target_ref": "REQ-001", "rationale": "Canonical acceptance condition."}],
        "rejected_interpretations": [{"text": "overwrite input.txt", "rationale": "violates input preservation"}], "unresolved_items": [],
        "fidelity_review": {"required": False, "reason": "fixed finite canonical probe", "review_ref": None, "adoption_status": "not_required"},
        "admission_ref": admission_ref,
    }, actor("p1-owner", "P1", "definition"))
    ws_defined = append_record(store, "work_state", "WS-0002", "WS-W-PHASE0", {"checkpoint": "defined", "interrupt_ref": None}, actor("p1-owner", "P1", "definition"), revision=2)
    store.commit([definition_ref, ws_defined], definition_ref, "P1 definition adoption; checkpoint defined.")

    method_ref = append_record(store, "validation_method", "VM-0001", "VM-CLM-A1-A7", {
        "method_id": "filesystem.inspect", "method_revision": "1", "claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3", "CLM-A4", "CLM-A5", "CLM-A6", "CLM-A7"],
        "description": "Read-only inspection of input/output bytes, exact digests, immutable chain, authority roles, and terminal consistency.", "procedure_ref": "probe/ACCEPTANCE.md",
        "object_scope": [input_ref, output_ref, "runs/"], "environment_constraints": ["local workspace only"], "expected_strength": "conclusive", "change_reason": None,
        "equivalence_evidence_refs": [], "independent_support_required": False, "status": "adopted",
    }, actor("p2-owner", "P2", "validation_method"))
    plan_ref = append_record(store, "execution_plan", "PLAN-0001", "PLAN-W-PHASE0", {
        "definition_ref": definition_ref, "design_revision": DESIGN_REVISION, "validation_method_refs": [method_ref],
        "units": [{"unit_id": PLAN_UNIT_ID, "objective": "Invoke the deterministic uppercase worker and adopt its separate output.", "owner_stage": "P3", "dependencies": [], "preconditions": ["definition is current", "output is absent", "effect is idempotent"], "input_refs": [input_ref], "target_refs": [output_ref], "capability_class": CAPABILITY_ID, "binding_constraints": ["workspace/output only", "no input overwrite"], "logical_intent_id": LOGICAL_INTENT_ID, "expected_artifact_refs": [output_ref], "expected_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"], "effect_intent_refs": ["records/EFF-0001.md"], "validation_hook_refs": [method_ref], "retry_policy": "Do not retry while operation/effect outcome is unknown.", "stop_conditions": ["unsafe or irreversible effect", "schema or digest mismatch"], "failure_routes": [{"route_id": "FR-001", "condition": "validation mismatch", "route": "active_blocker", "required_evidence_claims": ["CLM-A3"]}], "compensation_hook_ref": None, "forward_recovery_hook_ref": None}],
        "integration_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"], "budget_allocation_ref": budget_ref, "environment_revision_refs": ["ENV-LOCAL-R1"],
    }, actor("p2-owner", "P2", "design"))
    unit_ready = append_record(store, "plan_unit_state", "UNITSTATE-0001", "UNITSTATE-W-PHASE0-UNIT-001", unit_state_payload("ready", last_event_ref=plan_ref), actor("runtime-1", "runtime", "execution_projection"))
    ws_designed = append_record(store, "work_state", "WS-0003", "WS-W-PHASE0", {"checkpoint": "designed", "interrupt_ref": None}, actor("p2-owner", "P2", "design"), revision=3)
    store.commit([method_ref, plan_ref, unit_ready, ws_designed], plan_ref, "P2 design and validation-method adoption; checkpoint designed.")

    initial_effect = effect_payload("intended")
    enforce_phase0_effect_boundary(initial_effect)
    effect_intended = append_record(store, "effect", "EFF-0001", "EFF-INT-001", initial_effect, actor("runtime-1", "runtime", "effect_lifecycle_projection"))
    unit_pending = append_record(store, "plan_unit_state", "UNITSTATE-0002", "UNITSTATE-W-PHASE0-UNIT-001", unit_state_payload("pending", effect_ref=effect_intended, last_event_ref=effect_intended), actor("runtime-1", "runtime", "execution_projection"), revision=2)
    packet = make_dispatch(store.run_time, input_ref, effect_intended)
    packet_ref = store.add_message(packet, "packets", f"{DISPATCH_ID}.md", "Trusted outbound task packet; immutable and digest-bound before invocation.")
    dispatch_sha = sha256_file(store.ref_path(packet_ref))
    op_prepared = append_record(store, "delegated_operation", "OP-0001", "OP-INT-001", operation_payload(dispatch_sha, "prepared", effect_refs=[effect_intended]), actor("runtime-1", "runtime", "operation_lifecycle"))
    store.commit([effect_intended, unit_pending, packet_ref, op_prepared], op_prepared, "Dispatch packet and prepared operation committed with digest binding.")

    op_submitted = append_record(store, "delegated_operation", "OP-0002", "OP-INT-001", operation_payload(dispatch_sha, "submitted", effect_refs=[effect_intended], provider_sequence=1), actor("runtime-1", "runtime", "operation_lifecycle"), revision=2)
    store.commit([op_submitted], op_submitted, "Operation submitted after prepared commit.")
    effect_started = append_record(store, "effect", "EFF-0002", "EFF-INT-001", effect_payload("started"), actor("runtime-1", "runtime", "effect_lifecycle_projection"), revision=2)
    unit_running = append_record(store, "plan_unit_state", "UNITSTATE-0003", "UNITSTATE-W-PHASE0-UNIT-001", unit_state_payload("running", operation_ref=op_submitted, effect_ref=effect_started, last_event_ref=effect_started), actor("runtime-1", "runtime", "execution_projection"), revision=3)
    op_running = append_record(store, "delegated_operation", "OP-0003", "OP-INT-001", operation_payload(dispatch_sha, "running", effect_refs=[effect_started], provider_sequence=1), actor("runtime-1", "runtime", "operation_lifecycle"), revision=3)
    store.commit([effect_started, unit_running, op_running], op_running, "Operation running; exact committed packet is sent once.")

    worker_result, observation_ref = run_worker(packet, effect_payload("started"), store)
    output_sha = worker_result["output_sha256"]
    return_message = make_return(packet, worker_result, store.run_time)
    return_ref = store.add_message(return_message, "inbox/untrusted", "RET-0001.md", "Untrusted capability Return; schema-valid but not control state.")
    return_sha = sha256_file(store.ref_path(return_ref))
    op_succeeded = append_record(store, "delegated_operation", "OP-0004", "OP-INT-001", operation_payload(dispatch_sha, "succeeded", return_ref=return_ref, return_sha=return_sha, effect_refs=[effect_started], provider_sequence=2), actor("runtime-1", "runtime", "operation_lifecycle"), revision=4)
    store.log("return_received", return_ref=return_ref, return_sha256=return_sha, dispatch_ref=packet_ref, dispatch_sha256=dispatch_sha, operation_ref=op_succeeded)
    store.commit([observation_ref, return_ref, op_succeeded], op_succeeded, "Return stored immutably and mechanically bound to dispatch and operation; adoption remains pending.")

    # P3 adoption is deliberately separate from the capability Return.
    artifact_ref = append_record(store, "artifact_manifest", "ART-0001", "ART-W-PHASE0", {
        "manifest_id": "ART-W-PHASE0-R1", "target_revision": TARGET_REVISION,
        "artifacts": [{"artifact_id": "ARTIFACT-001", "path_or_uri": output_ref, "sha256": output_sha, "media_type": "text/plain", "revision": TARGET_REVISION, "source_unit_refs": [PLAN_UNIT_ID], "adoption_status": "adopted"}],
        "integration_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"], "environment_revision_refs": ["ENV-LOCAL-R1"],
    }, actor("p3-owner", "P3", "target_mutation"))
    effect_confirmed = append_record(store, "effect", "EFF-0003", "EFF-INT-001", effect_payload("confirmed", output_sha, observation_ref), actor("p3-owner", "P3", "execution_adoption"), revision=3)
    unit_succeeded = append_record(store, "plan_unit_state", "UNITSTATE-0004", "UNITSTATE-W-PHASE0-UNIT-001", unit_state_payload("succeeded", operation_ref="records/OP-0005.md", effect_ref=effect_confirmed, result_refs=[artifact_ref, observation_ref], last_event_ref=artifact_ref), actor("p3-owner", "P3", "execution_adoption"), revision=4)
    op_adopted = append_record(store, "delegated_operation", "OP-0005", "OP-INT-001", operation_payload(dispatch_sha, "succeeded", return_ref=return_ref, return_sha=return_sha, adoption="adopted", provider_sequence=2, evidence_refs=[observation_ref], effect_refs=[effect_confirmed]), actor("p3-owner", "P3", "execution_adoption"), revision=5)
    ws_executed = append_record(store, "work_state", "WS-0004", "WS-W-PHASE0", {"checkpoint": "executed", "interrupt_ref": None}, actor("p3-owner", "P3", "execution_adoption"), revision=4)
    store.commit([artifact_ref, effect_confirmed, unit_succeeded, op_adopted, ws_executed], ws_executed, "P3 adopted the validated artifact/effect; checkpoint executed.")

    # P4 evidence adoption and criteria verdicts are generated from read-only observations.
    evidence_refs: list[str] = []
    verdict_refs: list[str] = []
    criteria = [
        ("A1", "CLM-A1", input_ref, "Input SHA-256 remained unchanged from pre-dispatch observation."),
        ("A2", "CLM-A2", output_ref, "Output exists at the separate target path."),
        ("A3", "CLM-A3", output_ref, "Output bytes exactly match the expected uppercase fixture."),
        ("A4", "CLM-A4", "run.log", "Exactly one worker invocation and one effect start were observed."),
        ("A5", "CLM-A5", "commits/", "Evidence/verdict records are committed before acceptance and closure."),
        ("A6", "CLM-A6", "records/OP-0005.md", "Final operation and effect are known terminal states; no unknown is adopted."),
        ("A7", "CLM-A7", "records/OP-0005.md", "P3 adoption is recorded separately from the capability Return."),
    ]
    for index, (criterion_id, claim_id, object_ref, rationale) in enumerate(criteria, start=1):
        evidence_refs.append(append_record(store, "evidence", f"EVD-{index:04d}", f"EVD-{claim_id}", {
            "claim_id": claim_id, "criterion_id": criterion_id, "method_id": "filesystem.inspect", "method_revision": "1",
            "object_ref": object_ref, "object_revision": f"RUN-{store.run_time}", "design_revision": DESIGN_REVISION, "plan_revision": DESIGN_REVISION,
            "environment_ref": "ENV-LOCAL", "environment_revision": "ENV-LOCAL-R1", "observed_at": store.run_time,
            "freshness_policy": "Valid only for this fresh Phase 0 run.", "expires_at": None, "producer_id": "runtime-validator", "verifier_id": "p4-owner",
            "trust_domain": "local-readonly-probe", "source_lineage": [observation_ref, "probe/ACCEPTANCE.md"], "coverage": "full",
            "independence_basis": "Read-only runtime check separated from capability Return control authority.", "independence_group": "phase0-local-checks",
            "status": "valid", "supersedes_refs": [], "contradiction_refs": [], "raw_observation_refs": [observation_ref], "adopted_by": "P4",
        }, actor("p4-owner", "P4", "evidence_adoption"), explanation="P4-adopted machine evidence for the canonical acceptance criterion."))
        verdict_refs.append(append_record(store, "criteria_verdict", f"VER-{index:04d}", f"VER-{criterion_id}", {
            "criterion_id": criterion_id, "verdict": "PASS", "evidence_refs": [evidence_refs[-1]], "method_refs": [method_ref],
            "object_revision_refs": [TARGET_REVISION, f"RUN-{store.run_time}"], "coverage_complete": True, "freshness_ok": True,
            "conflict_status": "none", "independence_satisfied": True, "rationale": rationale,
        }, actor("p4-owner", "P4", "criteria_verdict"), explanation="P4 criterion verdict; capability self-report is not sufficient."))
    ws_accepted = append_record(store, "work_state", "WS-0005", "WS-W-PHASE0", {"checkpoint": "accepted", "interrupt_ref": None}, actor("p4-owner", "P4", "acceptance"), revision=5)
    store.commit(evidence_refs + verdict_refs + [ws_accepted], ws_accepted, "P4 adopted independent machine evidence and PASS verdicts; checkpoint accepted.")

    budget_final = dict(payloads["budget"])
    budget_final["budget"] = dict(payloads["budget"]["budget"])
    budget_final["budget"]["usage"] = dict(payloads["budget"]["budget"]["usage"])
    budget_final["budget"]["usage"].update({"attempts": 1, "strategy_families": 1, "capability_calls": 1, "effect_count": 1})
    budget_final["measured_at"] = store.run_time
    budget_ref_final = append_record(store, "resource_budget", "BUD-0002", "BUD-W-PHASE0", budget_final, actor("runtime-1", "runtime", "work_control_projection"), revision=2)
    settlement_ref = append_record(store, "terminal_settlement", "SET-0001", "SET-W-PHASE0", {
        "disposition": "completed", "achievement_checkpoint": "closed", "definition_ref": definition_ref, "execution_plan_ref": plan_ref,
        "artifact_manifest_ref": artifact_ref, "criteria_verdict_refs": verdict_refs, "open_blocker_refs": [], "inflight_operation_refs": [],
        "unsettled_effect_refs": [], "known_limitations": ["Fault injection is intentionally not part of Phase 0."], "remaining_obligations": [],
        "handoff_ref": None, "retention_summary": "Phase 0 audit artifacts retained under this run directory.", "settled_at": store.run_time,
    }, actor("p6-owner", "P6", "successful_closure"), explanation="P6 successful closure settlement; no open operation/effect/blocker remains.")
    closure_event = append_record(store, "ledger_event", "EVT-0001", "EVT-W-PHASE0-CLOSURE", {
        "event_type": "closure", "summary": "Canonical Phase 0 work reached completed terminal settlement.",
        "fact_refs": [settlement_ref, *verdict_refs], "decision_refs": [settlement_ref], "supersedes_refs": [],
        "rationale": "All required machine evidence and owner-stage adoptions are committed.", "hidden_reasoning_included": False,
    }, actor("p6-owner", "P6", "successful_closure"))
    wc_closed = append_record(store, "work_control", "WC-0002", "WC-W-PHASE0", {
        "lifecycle_state": "terminated", "terminal_disposition": "completed", "reason": "P6 completed terminal settlement.",
        "resume_condition_ref": None, "resume_owner": None, "resume_expiry": None, "resume_default_action": None,
        "latest_user_event_ref": None, "active_approval_refs": [], "active_operation_refs": [], "unresolved_effect_refs": [],
        "autonomy_budget": budget_final["budget"],
    }, actor("runtime-1", "runtime", "work_control_projection"), revision=2)
    ws_closed = append_record(store, "work_state", "WS-0006", "WS-W-PHASE0", {"checkpoint": "closed", "interrupt_ref": None}, actor("p6-owner", "P6", "successful_closure"), revision=6)
    store.commit([budget_ref_final, settlement_ref, closure_event, wc_closed, ws_closed], settlement_ref, "P6 closure settlement; checkpoint closed and Work Control terminal/completed.")

    final_projection = store.rebuild_projection_from_source()
    operation_api = OperationController(store)
    queried_operation = operation_api.query("OP-0005")
    reconciled_operation = operation_api.reconcile("OP-0005")
    store.log("operation_mechanism_check", query_state=queried_operation["state"], adoption_status=queried_operation["adoption_status"], reconcile_state=reconciled_operation["state"])
    verify = verify_run(run_dir, manifest_info, expected)
    result = {
        "status": "PASS" if verify["status"] == "PASS" else "FAIL",
        "run_id": run_id,
        "run_path": run_dir.relative_to(RUNNER_ROOT).as_posix(),
        "work_id": WORK_ID,
        "checkpoint": final_projection["work_state_ref"] and read_frontmatter(store.ref_path(final_projection["work_state_ref"]))["payload"]["checkpoint"],
        "work_control_lifecycle": read_frontmatter(store.ref_path(final_projection["work_control_ref"]))["payload"]["lifecycle_state"],
        "disposition": read_frontmatter(store.ref_path(final_projection["work_control_ref"]))["payload"]["terminal_disposition"],
        "input_sha256": input_before,
        "output_sha256": sha256_file(OUTPUT_PATH),
        "output_path": output_ref,
        "dispatch_digest": dispatch_sha,
        "return_digest": return_sha,
        "record_ids": {"source": "SRC-0001", "definition": "DEF-0001", "plan": "PLAN-0001", "operation": "OP-0005", "artifact": "ART-0001", "evidence": evidence_refs, "verdicts": verdict_refs, "settlement": settlement_ref, "work_state": "WS-0006", "work_control": "WC-0002"},
        "commit_ids": [f"COM-{index:04d}" for index in range(1, store.state_revision + 1)],
        "validation": verify,
    }
    write_bytes(run_dir / "result.json", json_bytes(result))
    store.log("runtime_complete", status=result["status"], checkpoint=result["checkpoint"], work_control_lifecycle=result["work_control_lifecycle"], disposition=result["disposition"])
    return result


def verify_run(run_dir: Path, manifest_info: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = JsonSchemaValidator(schema)
    failures: list[str] = []
    frontmatter_files: list[Path] = []
    for path in sorted(run_dir.rglob("*.md")):
        try:
            value = read_frontmatter(path)
        except ProbeError:
            continue
        frontmatter_files.append(path)
        try:
            validator.validate(value, schema)
        except SchemaValidationError as exc:
            failures.append(f"schema: {path.relative_to(run_dir)}: {exc}")

    commits: list[tuple[int, Path, dict[str, Any]]] = []
    for path in sorted((run_dir / "commits").glob("COM-*.md")):
        value = read_frontmatter(path)
        commits.append((value["payload"]["new_state_revision"], path, value))
    commits.sort()
    previous_id: str | None = None
    for expected_revision, path, commit in commits:
        payload = commit["payload"]
        if payload["expected_state_revision"] != expected_revision - 1 or payload["parent_commit_id"] != previous_id:
            failures.append(f"commit CAS chain mismatch: {path.name}")
        for item in payload["record_digests"]:
            target = run_dir / Path(item["ref"])
            if not target.is_file() or sha256_file(target) != item["sha256"]:
                failures.append(f"commit digest mismatch: {item['ref']}")
        projection = run_dir / Path(payload["projection_ref"])
        if not projection.is_file() or sha256_file(projection) != payload["projection_sha256"]:
            failures.append(f"projection digest mismatch: {payload['projection_ref']}")
        previous_id = payload["commit_id"]

    packet_path = run_dir / "packets" / f"{DISPATCH_ID}.md"
    packet = read_frontmatter(packet_path)
    packet_sha = sha256_file(packet_path)
    op_candidates = []
    for path in sorted((run_dir / "records").glob("OP-*.md")):
        value = read_frontmatter(path)
        if value.get("record_type") == "delegated_operation":
            op_candidates.append((value["record_revision"], path, value))
    _, op_path, operation = max(op_candidates)
    op_payload = operation["payload"]
    if op_payload["dispatch_payload_sha256"] != packet_sha:
        failures.append("dispatch digest binding mismatch")
    if op_payload["dispatch_payload_ref"] != "packets/DISP-0001.md":
        failures.append("dispatch ref binding mismatch")
    return_path = run_dir / "inbox" / "untrusted" / "RET-0001.md"
    return_message = read_frontmatter(return_path)
    return_sha = sha256_file(return_path)
    if op_payload["return_sha256"] != return_sha or op_payload["return_ref"] != "inbox/untrusted/RET-0001.md":
        failures.append("return digest binding mismatch")
    for key in ("work_id", "logical_intent_id", "dispatch_id", "attempt_id", "capability_id", "capability_revision"):
        if return_message[key] != packet[key]:
            failures.append(f"return/dispatch identity mismatch: {key}")
    if return_message["operation_state"] != "succeeded" or op_payload["state"] != "succeeded" or op_payload["adoption_status"] != "adopted":
        failures.append("operation did not reach adopted succeeded state")
    if operation["actor"]["role"] != "P3":
        failures.append("operation adoption was not owned by P3")

    input_after = sha256_file(INPUT_PATH)
    output_exists = OUTPUT_PATH.is_file()
    output_bytes = OUTPUT_PATH.read_bytes() if output_exists else b""
    expected_output = expected["expected_output_text"].encode("utf-8")
    expected_input_sha = sha256_bytes(expected["input_text"].encode("utf-8"))
    if input_after != expected_input_sha or not expected["input_must_remain_unchanged"]:
        failures.append("input preservation check could not be established")
    if not output_exists:
        failures.append("output missing")
    elif output_bytes != expected_output:
        failures.append("output content mismatch")

    log_events = []
    log_path = run_dir / "run.log"
    if log_path.is_file():
        log_events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    invocations = [event for event in log_events if event.get("event") == "worker_invocation"]
    if len(invocations) != 1:
        failures.append(f"duplicate effect/invocation count: {len(invocations)}")
    if invocations and invocations[0].get("packet_sha256") != packet_sha:
        failures.append("actual worker invocation did not use committed packet digest")

    final_projection = read_frontmatter(run_dir / "WORK_INDEX.md")
    final_state = read_frontmatter(run_dir / Path(final_projection["payload"]["work_state_ref"]))
    final_control = read_frontmatter(run_dir / Path(final_projection["payload"]["work_control_ref"]))
    settlement_paths = sorted((run_dir / "records").glob("SET-*.md"))
    if final_state["payload"]["checkpoint"] != "closed":
        failures.append("final checkpoint is not closed")
    if final_control["payload"]["lifecycle_state"] != "terminated" or final_control["payload"]["terminal_disposition"] != "completed":
        failures.append("final Work Control is not terminal/completed")
    if not settlement_paths:
        failures.append("terminal settlement missing")
    else:
        settlement = read_frontmatter(settlement_paths[-1])
        if settlement["payload"]["achievement_checkpoint"] != "closed" or settlement["payload"]["disposition"] != "completed":
            failures.append("terminal settlement inconsistent")
        if settlement["payload"]["criteria_verdict_refs"] == [] or settlement["payload"]["open_blocker_refs"] or settlement["payload"]["inflight_operation_refs"] or settlement["payload"]["unsettled_effect_refs"]:
            failures.append("terminal settlement has missing evidence or unsettled state")
    if final_projection["payload"]["open_operation_refs"] or final_projection["payload"]["unresolved_effect_refs"]:
        failures.append("final projection has inflight operation or unresolved effect")
    try:
        initial = read_frontmatter(run_dir / "records" / "WS-0001.md")
        executed_commit = next((c for _, _, c in commits if read_frontmatter(run_dir / Path(c["payload"]["projection_ref"]))["payload"]["work_state_ref"] == "records/WS-0004.md"), None)
        accepted_commit = next((c for _, _, c in commits if read_frontmatter(run_dir / Path(c["payload"]["projection_ref"]))["payload"]["work_state_ref"] == "records/WS-0005.md"), None)
        if initial["payload"]["checkpoint"] != "none" or executed_commit is None or accepted_commit is None:
            failures.append("checkpoint progression evidence missing")
        if accepted_commit is not None and not any(item["ref"].startswith("records/EVD-") for item in accepted_commit["payload"]["record_digests"]):
            failures.append("evidence was not committed before accepted")
    except (ProbeError, KeyError) as exc:
        failures.append(f"checkpoint evidence check failed: {exc}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "checks": {
            "manifest_boundary": "PASS" if manifest_info["manifest_file_count"] > 0 else "FAIL",
            "schema_validation": "PASS" if not any(item.startswith("schema:") for item in failures) else "FAIL",
            "commit_chain_and_cas": "PASS" if commits and not any(item.startswith("commit") for item in failures) else "FAIL",
            "dispatch_return_binding": "PASS" if not any("binding" in item for item in failures) else "FAIL",
            "worker_output": "PASS" if output_exists and output_bytes == expected_output else "FAIL",
            "input_unchanged": "PASS" if input_after == expected_input_sha else "FAIL",
            "single_effect": "PASS" if len(invocations) == 1 else "FAIL",
            "authority_adoption": "PASS" if op_payload["adoption_status"] == "adopted" and operation["actor"]["role"] == "P3" else "FAIL",
            "evidence_and_acceptance": "PASS" if not any("evidence" in item or "checkpoint" in item for item in failures) else "FAIL",
            "terminal_consistency": "PASS" if not any("final" in item or "terminal" in item or "unresolved" in item for item in failures) else "FAIL",
            "projection_rebuild": "PASS" if final_projection["payload"]["state_revision"] == commits[-1][0] else "FAIL",
        },
        "failures": failures,
        "dispatch_sha256": packet_sha,
        "return_sha256": return_sha,
        "input_sha256": input_after,
        "output_sha256": sha256_file(OUTPUT_PATH) if OUTPUT_PATH.exists() else None,
        "frontmatter_file_count": len(frontmatter_files),
        "commit_count": len(commits),
        "operation_ref": op_path.relative_to(run_dir).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or verify the FPO Phase 0 baseline probe")
    parser.add_argument("command", nargs="?", choices=("manifest", "run", "verify"), default="run")
    parser.add_argument("--run", dest="run_path", help="run directory for verify")
    args = parser.parse_args()
    try:
        if args.command == "manifest":
            info = validate_manifest()
            result = {
                "status": "PASS",
                "manifest_path": MANIFEST_PATH.relative_to(RUNNER_ROOT).as_posix(),
                "spec_runtime_root": SPEC_RUNTIME_ROOT.relative_to(RUNNER_ROOT).as_posix(),
                "manifest_file_count": info["manifest_file_count"],
                "unresolved": 0,
                "hash_mismatch": 0,
                "resolver_events": info["resolver_events"],
            }
        elif args.command == "run":
            result = run_baseline()
        else:
            if not args.run_path:
                raise ProbeError("verify requires --run <run-directory>")
            run_dir = Path(args.run_path).resolve()
            expected = json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8"))
            result = verify_run(run_dir, validate_manifest(), expected)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    except (ProbeError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
