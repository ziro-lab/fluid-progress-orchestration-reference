#!/usr/bin/env python3
"""Static, schema, fixture, and deterministic invariant checks for FPO v0.2.

This script validates the design bundle. It does not execute an LLM agent,
external capability, real side effect, or real crash/concurrency mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable
import copy
import hashlib
import json
import re
import sys
import os
import subprocess
import tempfile

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
VALIDATION = ROOT / "validation"
EXAMPLE = ROOT / "examples/canonical_work/W-EXAMPLE"
SCHEMA_PATH = RUNTIME / "schemas/fpo_records.schema.json"

ALLOWED_CHECKPOINTS = ["none", "defined", "designed", "executed", "accepted", "closed"]
WORK_LIFECYCLE = ["active", "suspended", "canceling", "terminated", "archived"]
TERMINAL_DISPOSITIONS = ["completed", "canceled", "aborted", "unsatisfiable", "out_of_budget", "safety_stop", "out_of_scope"]
OPERATION_STATES = ["prepared", "submitted", "running", "waiting_input", "waiting_authorization", "succeeded", "failed", "rejected", "timed_out", "canceled", "unknown"]
EFFECT_STATES = ["intended", "started", "confirmed", "failed", "unknown", "compensating", "compensated", "compensation_failed", "forward_recovery_required"]
BLOCKER_STATES = ["open", "investigating", "waiting", "resolved", "superseded"]
EVIDENCE_STATES = ["proposed", "valid", "superseded", "contradicted", "retracted"]
UNIT_STATES = ["pending", "ready", "running", "blocked", "succeeded", "failed", "skipped", "superseded"]
RISK_TIERS = ["T0", "T1", "T2", "T3"]
EXPECTED_RECORD_TYPES = {
    "work_state", "work_control", "source_request", "work_admission", "work_definition",
    "validation_method", "execution_plan", "plan_unit_state", "blocker_set", "blocker",
    "progress_claim", "delegated_operation", "evidence", "criteria_verdict", "effect",
    "capability_entry", "approval", "resource_budget", "artifact_manifest", "control_event",
    "current_projection", "ledger_event", "terminal_settlement", "commit",
}
EXPECTED_MESSAGE_TYPES = {"dispatch_packet", "capability_return"}
LEGACY_NAMES = {
    "DISPATCH_RETURN_CONTRACT.md", "CAPABILITY_REGISTRY_CONTRACT.md",
    "P5_修正・例外ハーネス.md", "J3_P5回復経路判断ハーネス.md",
    "M07_例外・引き継ぎ.md", "P6_終了・資産化ハーネス.md", "STATIC_REVIEW.md",
}
GENERATED_REPORTS = {
    "validation/STATIC_INTEGRITY_CHECK.md",
    "validation/MODEL_CHECK_REPORT.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"Unclosed front matter: {path}")
    return yaml.safe_load(text[4:end]) or {}


@dataclass
class Check:
    check_id: str
    status: str
    detail: str


def add(out: list[Check], check_id: str, ok: bool, pass_detail: str, fail_detail: str) -> None:
    out.append(Check(check_id, "PASS" if ok else "FAIL", pass_detail if ok else fail_detail))


def runtime_manifest_checks(out: list[Check]) -> tuple[dict[str, Any], set[str]]:
    manifest_path = RUNTIME / "RUNTIME_MANIFEST.md"
    try:
        manifest = front_matter(manifest_path)
        ok = manifest.get("doc_type") == "FPO.RUNTIME_MANIFEST" and str(manifest.get("schema_version")) == "0.2"
        entries = manifest.get("files", [])
        ok = ok and isinstance(entries, list) and bool(entries)
        add(out, "S-01", ok, f"Runtime Manifest parsed: {len(entries)} entries", f"Invalid Runtime Manifest: {manifest}")
    except Exception as exc:
        out.append(Check("S-01", "FAIL", str(exc)))
        return {}, set()

    entry_paths = {e.get("path") for e in entries if isinstance(e, dict) and e.get("path")}
    actual_runtime = {
        p.relative_to(RUNTIME).as_posix()
        for p in RUNTIME.rglob("*")
        if p.is_file() and p.name != "RUNTIME_MANIFEST.md" and p.suffix in {".md", ".json"}
    }
    add(out, "S-02", entry_paths == actual_runtime,
        "Manifest exactly covers all normative runtime Markdown/JSON files",
        f"missing={sorted(actual_runtime-entry_paths)} extra={sorted(entry_paths-actual_runtime)}")

    bad_hash = []
    for e in entries:
        p = RUNTIME / e["path"]
        if not p.exists() or sha256(p) != e.get("sha256"):
            bad_hash.append(e["path"])
    add(out, "S-03", not bad_hash, "Runtime file hashes match", f"Hash mismatch: {bad_hash}")

    bad_zone = [p for p in entry_paths if p.startswith(("docs/", "validation/", "review/", "extensions/", "examples/"))]
    add(out, "S-04", not bad_zone, "Runtime and development contexts are physically separated", f"Non-runtime files listed: {bad_zone}")
    return manifest, entry_paths


def static_checks() -> list[Check]:
    out: list[Check] = []
    manifest, entry_paths = runtime_manifest_checks(out)
    if not manifest:
        return out

    required = {
        "RUNTIME_ENTRY.md", "core/00_最小常駐核.md", "core/WORK_STATE.md",
        "core/J1_段階判断ハーネス.md", "core/J2_P2必要知識判断ハーネス.md",
        "core/J3_P5必要知識・能力判断ハーネス.md", "core/P1_作業定義ハーネス.md",
        "core/P2_作業設計ハーネス.md", "core/P3_実行ハーネス.md",
        "core/P4_検証ハーネス.md", "core/P5_進行回復ハーネス.md",
        "core/P6_終了・引き渡しハーネス.md", "contracts/AUTHORITY_MATRIX.md",
        "contracts/WORK_DEFINITION_CONTRACT.md", "contracts/EXECUTION_PLAN_CONTRACT.md",
        "contracts/WORK_CONTROL_CONTRACT.md", "contracts/DELEGATED_OPERATION_CONTRACT.md",
        "contracts/ACTIVE_BLOCKER_CONTRACT.md", "contracts/EVIDENCE_CONTRACT.md",
        "contracts/EFFECT_RECOVERY_CONTRACT.md", "contracts/TRUST_AND_CAPABILITY_CONTRACT.md",
        "contracts/実行基盤契約.md", "schemas/fpo_records.schema.json",
    }
    missing = sorted(required-entry_paths)
    add(out, "S-05", not missing, "All hardening core/contracts/schema are present", f"Missing required: {missing}")

    runtime_text = "\n".join((RUNTIME/p).read_text(encoding="utf-8") for p in sorted(entry_paths) if (RUNTIME/p).suffix == ".md")
    legacy_hits = sorted(x for x in LEGACY_NAMES if x in runtime_text)
    add(out, "S-06", not legacy_hits, "No legacy normative references", f"Legacy refs: {legacy_hits}")

    basenames = {Path(p).name for p in entry_paths} | {"RUNTIME_MANIFEST.md"}
    unresolved: list[str] = []
    for rel in sorted(entry_paths):
        p = RUNTIME/rel
        if p.suffix != ".md":
            continue
        text = p.read_text(encoding="utf-8")
        for raw in re.findall(r"`([^`\n]+\.(?:md|json)(?:#[^`\n]+)?)`", text):
            ref_text = raw.split("#", 1)[0]
            direct = (p.parent/ref_text).resolve()
            inside = str(direct).startswith(str(RUNTIME.resolve()))
            external_aliases={"WORK_STATE.md","WORK_CONTROL.md","WORK_INDEX.md"}
            if not (inside and direct.exists()) and Path(ref_text).name not in basenames and Path(ref_text).name not in external_aliases:
                unresolved.append(f"{rel} -> {raw}")
    add(out, "S-07", not unresolved, "Runtime Markdown/JSON references resolve", "; ".join(unresolved[:30]))

    ws = (RUNTIME/"core/WORK_STATE.md").read_text(encoding="utf-8")
    j1 = (RUNTIME/"core/J1_段階判断ハーネス.md").read_text(encoding="utf-8")
    cp_ok = all(f"`{cp}`" in ws for cp in ALLOWED_CHECKPOINTS)
    route_ok = all(cp in j1 for cp in ALLOWED_CHECKPOINTS)
    banned = [x for x in ["WAIT", "FAILED", "CANCELED", "NO_PROGRESS"] if re.search(rf"checkpoint\s*[=:]\s*`?{x}", runtime_text, re.I)]
    add(out, "S-08", cp_ok and route_ok and not banned, "Six Achievement checkpoints preserved", f"cp_ok={cp_ok} route_ok={route_ok} banned={banned}")

    expected_owners = {
        "routing":"J1", "definition":"P1", "design":"P2", "validation_method":"P2",
        "target_mutation":"P3", "execution_adoption":"P3", "criteria_verdict":"P4",
        "evidence_adoption":"P4", "acceptance":"P4", "predefined_validation_route":"P4",
        "blocker_case":"P5", "recovery_rollback_adoption":"P5", "successful_closure":"P6",
        "work_control_projection":"runtime", "operation_lifecycle":"runtime",
        "effect_lifecycle_projection":"runtime", "durable_commit":"runtime",
    }
    authority = front_matter(RUNTIME/"contracts/AUTHORITY_MATRIX.md").get("authority_owners", {})
    add(out, "S-09", authority == expected_owners, "Critical Authority owners are explicit and non-conflicting", f"Authority mismatch: {authority}")

    contracts = sorted((RUNTIME/"contracts").glob("*.md"))
    unversioned = [p.name for p in contracts if p.name != "AUTHORITY_MATRIX.md" and "contract 0.2" not in p.read_text(encoding="utf-8")]
    add(out, "S-10", not unversioned, "Operational contracts declare contract 0.2", f"Missing contract marker: {unversioned}")

    p5 = (RUNTIME/"core/P5_進行回復ハーネス.md").read_text(encoding="utf-8")
    p5_ok = "P5自身がTargetを変更した状態で`executed`を維持してはならない" in p5 and "P5はcheckpointを前進させない" in p5
    add(out, "S-11", p5_ok, "P5 target-mutation and forward-checkpoint guards present", "P5 guard text missing")

    p6 = (RUNTIME/"core/P6_終了・引き渡しハーネス.md").read_text(encoding="utf-8")
    p6_ok = "資産化はclosure条件に含めない" in p6 and "M08_資産化・成長" not in p6 and "lifecycle = terminated" in p6
    add(out, "S-12", p6_ok, "Closure is settled without assetization and terminates Work Control", "P6 closure deletion/terminal test failed")

    issue_matrix = (ROOT/"docs/ISSUE_CLOSURE_MATRIX.md").read_text(encoding="utf-8")
    issue_ids = [f"B-{i:02d}" for i in range(1,13)] + [f"H-{i:02d}" for i in range(1,11)]
    missing_issues = [i for i in issue_ids if i not in issue_matrix]
    add(out, "S-13", not missing_issues, "All BLOCKER/HIGH review findings mapped", f"Missing issue mappings: {missing_issues}")

    # JSON Schema validity and required vocabulary.
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        top_types = {
            branch["$ref"].rsplit("/", 1)[-1]
            for branch in schema.get("oneOf", [])
            if isinstance(branch, dict) and isinstance(branch.get("$ref"), str)
        }
        expected_top_types = EXPECTED_RECORD_TYPES | EXPECTED_MESSAGE_TYPES
        schema_ok = top_types == expected_top_types
        add(
            out,
            "S-14",
            schema_ok,
            f"JSON Schema valid with {len(EXPECTED_RECORD_TYPES)} record types + {len(EXPECTED_MESSAGE_TYPES)} boundary messages",
            f"Top-level schema mismatch missing={sorted(expected_top_types-top_types)} extra={sorted(top_types-expected_top_types)}",
        )
    except Exception as exc:
        schema = {}
        out.append(Check("S-14", "FAIL", f"JSON Schema invalid: {exc}"))

    # Canonical fixtures: all machine front matter validates; malicious control-like return is rejected.
    fixture_fail: list[str] = []
    fixture_count = 0
    if schema:
        validator = jsonschema.Draft202012Validator(schema)
        raw_return = None
        raw_dispatch = None
        fixture_types: set[str] = set()
        for p in sorted((ROOT/"examples").rglob("*.md")):
            data = front_matter(p)
            if not data:
                continue
            if data.get("schema_name") == "fpo.record":
                fixture_types.add(str(data.get("record_type")))
            elif data.get("schema_name") in {"fpo.dispatch_packet", "fpo.capability_return"}:
                fixture_types.add(str(data.get("message_type")))
            else:
                continue
            fixture_count += 1
            errors = list(validator.iter_errors(data))
            if errors:
                fixture_fail.append(f"{p.relative_to(ROOT)}: {errors[0].message}")
            if data.get("schema_name") == "fpo.capability_return":
                raw_return = data
            if data.get("schema_name") == "fpo.dispatch_packet":
                raw_dispatch = data
        expected_fixture_types = EXPECTED_RECORD_TYPES | EXPECTED_MESSAGE_TYPES
        for missing_type in sorted(expected_fixture_types - fixture_types):
            fixture_fail.append(f"missing top-level fixture: {missing_type}")
        for extra_type in sorted(fixture_types - expected_fixture_types):
            fixture_fail.append(f"unknown top-level fixture: {extra_type}")
        if raw_return:
            injected = copy.deepcopy(raw_return)
            injected["checkpoint"] = "closed"
            if not list(validator.iter_errors(injected)):
                fixture_fail.append("capability_return accepted injected checkpoint")
        else:
            fixture_fail.append("no capability_return fixture")
        if raw_dispatch:
            injected = copy.deepcopy(raw_dispatch)
            injected["checkpoint"] = "closed"
            if not list(validator.iter_errors(injected)):
                fixture_fail.append("dispatch_packet accepted injected checkpoint")
        else:
            fixture_fail.append("no dispatch_packet fixture")
    add(out, "S-15", not fixture_fail, f"Canonical fixtures schema-valid ({fixture_count}) and boundary-message control injection rejected", "; ".join(fixture_fail[:10]))

    # Canonical commit digests and refs.
    digest_fail: list[str] = []
    try:
        commit = front_matter(EXAMPLE/"commits/COM-0001.md")
        payload = commit["payload"]
        for e in payload["record_digests"]:
            p = EXAMPLE/e["ref"]
            if not p.exists() or sha256(p) != e["sha256"]:
                digest_fail.append(e["ref"])
        pp = EXAMPLE/payload["projection_ref"]
        if not pp.exists() or sha256(pp) != payload["projection_sha256"]:
            digest_fail.append(payload["projection_ref"])
        adopted_files = {
            p.relative_to(EXAMPLE).as_posix()
            for folder in ["global","records","packets","projections","observations"]
            for p in (EXAMPLE/folder).rglob("*") if p.is_file()
        }
        listed = {e["ref"] for e in payload["record_digests"]}
        if adopted_files != listed:
            digest_fail.append(f"coverage missing={sorted(adopted_files-listed)} extra={sorted(listed-adopted_files)}")
    except Exception as exc:
        digest_fail.append(str(exc))
    add(out, "S-16", not digest_fail, "Canonical semantic Commit covers and hashes all adopted fixture inputs", f"Commit fixture failures: {digest_fail}")

    # Contract/schema enum alignment.
    enum_checks = [
        ("WORK_CONTROL_CONTRACT.md", WORK_LIFECYCLE + TERMINAL_DISPOSITIONS),
        ("DELEGATED_OPERATION_CONTRACT.md", OPERATION_STATES),
        ("EFFECT_RECOVERY_CONTRACT.md", EFFECT_STATES),
        ("ACTIVE_BLOCKER_CONTRACT.md", BLOCKER_STATES),
        ("EVIDENCE_CONTRACT.md", EVIDENCE_STATES),
        ("EXECUTION_PLAN_CONTRACT.md", UNIT_STATES),
    ]
    missing_vocab=[]
    for name,words in enum_checks:
        text=(RUNTIME/"contracts"/name).read_text(encoding="utf-8")
        for word in words:
            if word not in text:
                missing_vocab.append(f"{name}:{word}")
    if schema:
        defs=schema["$defs"]
        expected_schema_enums={
            "checkpoint":ALLOWED_CHECKPOINTS,"risk_tier":RISK_TIERS,"terminal_disposition":TERMINAL_DISPOSITIONS,
            "operation_state":OPERATION_STATES,"effect_state":EFFECT_STATES,"blocker_status":BLOCKER_STATES,
            "evidence_status":EVIDENCE_STATES,"unit_state":UNIT_STATES,
        }
        for name,vals in expected_schema_enums.items():
            if defs.get(name,{}).get("enum") != vals:
                missing_vocab.append(f"schema:{name}")
    add(out, "S-17", not missing_vocab, "Contract and machine-schema state vocabularies align", f"Vocabulary mismatch: {missing_vocab}")

    risk_text=(RUNTIME/"contracts/WORK_CONTROL_CONTRACT.md").read_text(encoding="utf-8")
    risk_ok=all(f"`{r}`" in risk_text for r in RISK_TIERS) and "自律P3実行範囲外" in risk_text
    add(out, "S-18", risk_ok, "Risk Tier T0–T3 and T3 autonomy boundary are normative", "Risk tier boundary incomplete")

    all_nonreview_md="\n".join(
        p.read_text(encoding="utf-8") for p in ROOT.rglob("*.md")
        if "review/" not in p.relative_to(ROOT).as_posix()
        and p.relative_to(ROOT).as_posix() not in GENERATED_REPORTS
    )
    obsolete=[]
    for token, pattern in [("desired_mode", r"\bdesired_mode\b"),("observed_mode", r"\bobserved_mode\b"),("waiting_auth", r"\bwaiting_auth\b")]:
        if re.search(pattern, all_nonreview_md):
            obsolete.append(token)
    add(out, "S-19", not obsolete, "No obsolete v0.1 operational vocabulary outside frozen review", f"Obsolete vocabulary: {obsolete}")

    root_manifest=ROOT/"BUNDLE_MANIFEST.md"
    if not root_manifest.exists():
        out.append(Check("S-20","SKIP","Root bundle manifest not generated yet"))
    else:
        failures=[]
        try:
            data=front_matter(root_manifest)
            exclusions=set(data.get("generated_exclusions",[]))
            if exclusions != GENERATED_REPORTS:
                failures.append(f"generated_exclusions={sorted(exclusions)}")
            listed={e["path"] for e in data.get("files",[])}
            actual={
                p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()
                and p.name != "BUNDLE_MANIFEST.md" and p.relative_to(ROOT).as_posix() not in exclusions
                and "__pycache__" not in p.parts and p.suffix != ".pyc"
            }
            if listed != actual:
                failures.append(f"coverage missing={sorted(actual-listed)} extra={sorted(listed-actual)}")
            for e in data.get("files",[]):
                p=ROOT/e["path"]
                if not p.exists() or sha256(p)!=e["sha256"]:
                    failures.append(e["path"])
        except Exception as exc:
            failures.append(str(exc))
        add(out, "S-20", not failures, "Full immutable bundle manifest matches (generated reports excluded by contract)", f"Bundle manifest failures: {failures[:10]}")

    trust_text=(RUNTIME/"contracts/TRUST_AND_CAPABILITY_CONTRACT.md").read_text(encoding="utf-8")
    runtime_contract=(RUNTIME/"contracts/実行基盤契約.md").read_text(encoding="utf-8")
    trust_terms=["Trusted Control", "Untrusted Inbox", "schema", "least privilege", "Secret Store", "sandbox", "network egress"]
    trust_missing=[x for x in trust_terms if x not in trust_text and x not in runtime_contract]
    add(out, "S-21", not trust_missing, "Trust zones, schema gate, least privilege, secret handles, sandbox, and egress controls are normative", f"Missing trust controls: {trust_missing}")

    p1_text=(RUNTIME/"core/P1_作業定義ハーネス.md").read_text(encoding="utf-8")
    wd_text=(RUNTIME/"contracts/WORK_DEFINITION_CONTRACT.md").read_text(encoding="utf-8")
    schema_defs=schema.get("$defs",{}) if schema else {}
    wd_props=schema_defs.get("payload_work_definition",{}).get("properties",{})
    intent_fields={"source_request_refs","coverage","decision_priorities","assumptions","design_discretion","rejected_interpretations","fidelity_review"}
    intent_ok=intent_fields.issubset(wd_props) and all(x in (p1_text+wd_text) for x in ["coverage","Decision","Source"])
    add(out, "S-22", intent_ok, "Intent Fidelity has immutable source, coverage, assumptions, discretion, and decision policy", f"Intent fields/text incomplete: {sorted(intent_fields-set(wd_props))}")

    entry_text=(RUNTIME/"RUNTIME_ENTRY.md").read_text(encoding="utf-8")
    context_ok=all(x in entry_text for x in ["docs/", "review/", "validation/", "examples/", "extensions/"]) and "Control Context" in entry_text and "JSON Schema" in entry_text
    add(out, "S-23", context_ok, "Runtime Control Context excludes development/review/fixture material and full schema loading", "Runtime context separation guard incomplete")

    dispatch_fail=[]
    try:
        packet_path=EXAMPLE/"packets/DISP-0001.md"
        packet=front_matter(packet_path)
        op=front_matter(EXAMPLE/"records/OP-0001.md")
        opp=op["payload"]
        if packet.get("schema_name")!="fpo.dispatch_packet" or packet.get("message_type")!="dispatch_packet": dispatch_fail.append("packet schema/message")
        if opp.get("dispatch_payload_ref")!="packets/DISP-0001.md": dispatch_fail.append("operation dispatch ref")
        if opp.get("dispatch_payload_sha256")!=sha256(packet_path): dispatch_fail.append("operation dispatch digest")
        for key in ["dispatch_id","work_id","logical_intent_id","attempt_id","plan_unit_id","owner_stage","capability_id","capability_revision","binding_ref","target_revision_ref"]:
            op_key={"work_id":"work_id"}.get(key,key)
            op_value=op.get("work_id") if key=="work_id" else opp.get(op_key)
            if packet.get(key)!=op_value: dispatch_fail.append(f"packet/operation {key}")
    except Exception as exc:
        dispatch_fail.append(str(exc))
    add(out, "S-24", not dispatch_fail, "Canonical outbound Dispatch Packet is schema-valid, identity-matched, and digest-bound to Operation", f"Dispatch binding failures: {dispatch_fail}")

    projection_fail=[]
    try:
        budget=front_matter(EXAMPLE/"records/BUD-0001.md")
        unit=front_matter(EXAMPLE/"records/UNITSTATE-0001.md")
        wc=front_matter(EXAMPLE/"records/WC-0001.md")
        proj=front_matter(EXAMPLE/"projections/PROJ-0001.md")
        pp=proj["payload"]
        if pp.get("budget_ref")!="records/BUD-0001.md": projection_fail.append("budget_ref")
        if wc["payload"].get("autonomy_budget")!=budget["payload"].get("budget"): projection_fail.append("budget projection mismatch")
        if pp.get("unit_state_refs")!=["records/UNITSTATE-0001.md"]: projection_fail.append("unit_state_refs")
        cached=next((x for x in pp.get("unit_states",[]) if x.get("unit_id")==unit["payload"].get("unit_id")),None)
        if not cached: projection_fail.append("unit cache missing")
        else:
            pairs={"state":"state","operation_refs":"operation_refs","effect_refs":"effect_refs","adopted_result_refs":"adopted_result_refs","last_event_ref":"last_event_ref"}
            for ck,uk in pairs.items():
                if cached.get(ck)!=unit["payload"].get(uk): projection_fail.append(f"unit projection {ck}")
    except Exception as exc:
        projection_fail.append(str(exc))
    add(out, "S-25", not projection_fail, "Immutable Budget/Unit records are the source; Work Control/Current Projection caches agree", f"Projection/source failures: {projection_fail}")

    schema_gen_fail=[]
    try:
        with tempfile.TemporaryDirectory() as td:
            generated=Path(td)/"fpo_records.schema.json"
            env=dict(os.environ)
            env["FPO_SCHEMA_OUT"]=str(generated)
            proc=subprocess.run([sys.executable,str(VALIDATION/"generate_schema.py")],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
            if proc.returncode!=0: schema_gen_fail.append(proc.stderr or proc.stdout)
            elif generated.read_bytes()!=SCHEMA_PATH.read_bytes(): schema_gen_fail.append("generated schema differs from normative schema")
    except Exception as exc:
        schema_gen_fail.append(str(exc))
    add(out, "S-26", not schema_gen_fail, "Normative JSON Schema is reproducibly generated from checked-in source", f"Schema generation failures: {schema_gen_fail}")

    # Negative schema guards: contradictory lifecycle/authority states must fail closed.
    schema_guard_fail: list[str] = []
    if schema:
        validator = jsonschema.Draft202012Validator(schema)

        def expect_rejected(label: str, source: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
            try:
                candidate = copy.deepcopy(front_matter(source))
                mutate(candidate)
                if not list(validator.iter_errors(candidate)):
                    schema_guard_fail.append(label)
            except Exception as exc:
                schema_guard_fail.append(f"{label}: {exc}")

        expect_rejected("closed work with active blocker", EXAMPLE/"records/WS-0001.md",
                        lambda d: d["payload"].update({"checkpoint":"closed","interrupt_ref":"records/BLKSET-0001.md"}))
        expect_rejected("active work with terminal disposition", EXAMPLE/"records/WC-0001.md",
                        lambda d: d["payload"].update({"lifecycle_state":"active","terminal_disposition":"completed"}))
        expect_rejected("suspended work without resume metadata", EXAMPLE/"records/WC-0001.md",
                        lambda d: d["payload"].update({"lifecycle_state":"suspended"}))
        expect_rejected("return ref without return digest", EXAMPLE/"records/OP-0001.md",
                        lambda d: d["payload"].update({"return_sha256":None}))
        expect_rejected("waiting_input without request ref", EXAMPLE/"records/OP-0001.md",
                        lambda d: d["payload"].update({"state":"waiting_input","input_request_ref":None}))
        expect_rejected("valid Evidence without owner adoption", EXAMPLE/"records/EVD-0001.md",
                        lambda d: d["payload"].update({"status":"valid","adopted_by":None}))
        expect_rejected("PASS verdict without complete Evidence", EXAMPLE/"records/VER-0001.md",
                        lambda d: d["payload"].update({"verdict":"PASS","evidence_refs":[],"coverage_complete":False}))
        expect_rejected("idempotent Effect without key", EXAMPLE/"records/EFF-0001.md",
                        lambda d: d["payload"].update({"idempotency_key":None}))
        expect_rejected("revoked Approval without revocation ref", EXAMPLE/"records/APR-0001.md",
                        lambda d: d["payload"].update({"status":"revoked","revocation_ref":None}))
        expect_rejected("admissible T3 work", EXAMPLE/"records/ADM-0001.md",
                        lambda d: d["payload"].update({"admissible":True,"risk_tier":"T3"}))
        expect_rejected("completed settlement with unsettled Effect", ROOT/"examples/schema_fixtures/SET-0001.md",
                        lambda d: d["payload"].update({"unsettled_effect_refs":["records/EFF-OPEN.md"]}))
    add(out, "S-27", not schema_guard_fail, "Contradictory lifecycle, Evidence, Effect, Approval, admission, and settlement records fail schema validation", f"Schema guards accepted invalid states: {schema_guard_fail}")

    # Canonical cross-record graph: individual valid documents must also describe one coherent state.
    graph_fail: list[str] = []
    try:
        def load_rel(ref: str) -> dict[str, Any]:
            clean = ref.split("#", 1)[0]
            return front_matter(EXAMPLE/clean)

        records = {p.relative_to(EXAMPLE).as_posix(): front_matter(p) for p in sorted((EXAMPLE/"records").glob("*.md"))}
        projection = front_matter(EXAMPLE/"projections/PROJ-0001.md")
        commit = front_matter(EXAMPLE/"commits/COM-0001.md")
        packet = front_matter(EXAMPLE/"packets/DISP-0001.md")
        raw_return_path = EXAMPLE/"inbox/untrusted/RETURN-raw-0001.md"
        raw_return = front_matter(raw_return_path)
        capability = front_matter(EXAMPLE/"global/CAP-0001.md")
        by_type = {d["record_type"]: d for d in records.values()}
        pp, cp = projection["payload"], commit["payload"]

        work_docs = list(records.values()) + [projection, commit]
        if {d.get("work_id") for d in work_docs} != {"W-EXAMPLE"}: graph_fail.append("work_id divergence")
        sequences = [d.get("sequence") for d in work_docs]
        if len(sequences) != len(set(sequences)): graph_fail.append("duplicate work sequence")
        if cp.get("commit_id") != pp.get("current_commit_id"): graph_fail.append("projection/commit identity")
        if cp.get("new_state_revision") != pp.get("state_revision"): graph_fail.append("projection/commit state revision")
        if cp.get("projection_ref") != "projections/PROJ-0001.md": graph_fail.append("commit projection ref")

        ws, wc = by_type["work_state"]["payload"], by_type["work_control"]["payload"]
        if ws.get("interrupt_ref") != pp.get("active_blocker_set_ref"): graph_fail.append("WORK_STATE/blocker set projection")
        if set(wc.get("active_operation_refs", [])) != set(pp.get("open_operation_refs", [])): graph_fail.append("operation projection")
        if set(wc.get("unresolved_effect_refs", [])) != set(pp.get("unresolved_effect_refs", [])): graph_fail.append("effect projection")
        if set(wc.get("active_approval_refs", [])) != set(pp.get("active_approval_refs", [])): graph_fail.append("approval projection")

        blkset = by_type["blocker_set"]["payload"]
        blockers = [load_rel(r)["payload"] for r in blkset.get("active_blocker_refs", [])]
        active_blockers = [b for b in blockers if b.get("status") not in {"resolved", "superseded"}]
        waiting_blockers = [b for b in active_blockers if b.get("status") == "waiting"]
        if blkset.get("blocking_count") != len(active_blockers): graph_fail.append("blocker count")
        if blkset.get("waiting_count") != len(waiting_blockers): graph_fail.append("waiting blocker count")

        op, effect = by_type["delegated_operation"]["payload"], by_type["effect"]["payload"]
        plan, approval = by_type["execution_plan"]["payload"], by_type["approval"]["payload"]
        unit = next((u for u in plan.get("units", []) if u.get("unit_id") == op.get("plan_unit_id")), None)
        if unit is None: graph_fail.append("Operation has no Plan Unit")
        else:
            if unit.get("logical_intent_id") != op.get("logical_intent_id"): graph_fail.append("Operation logical intent")
            if unit.get("logical_intent_id") != effect.get("logical_intent_id") or unit.get("unit_id") != effect.get("plan_unit_id"): graph_fail.append("Effect/Plan identity")
            if "records/EFF-0001.md" not in unit.get("effect_intent_refs", []): graph_fail.append("Plan Effect ref")
        if op.get("dispatch_payload_sha256") != sha256(EXAMPLE/op["dispatch_payload_ref"]): graph_fail.append("Dispatch digest")
        if op.get("return_sha256") != sha256(raw_return_path): graph_fail.append("Return digest")
        for key in ["work_id", "logical_intent_id", "dispatch_id", "attempt_id", "capability_id", "capability_revision"]:
            expected = packet.get(key)
            observed = raw_return.get(key)
            op_value = by_type["delegated_operation"].get("work_id") if key == "work_id" else op.get(key)
            if expected != observed or expected != op_value: graph_fail.append(f"Dispatch/Return/Operation {key}")
        cap = capability["payload"]
        if cap.get("capability_id") != op.get("capability_id") or cap.get("capability_revision") != op.get("capability_revision"): graph_fail.append("Capability binding identity")
        if cap.get("provider_identity") != raw_return.get("provider_identity") or cap.get("binding_ref") != op.get("binding_ref"): graph_fail.append("Capability provider/binding")
        if approval.get("status") != "granted" or effect.get("effect_class") not in approval.get("allowed_effect_classes", []): graph_fail.append("Effect approval class")
        if effect.get("target_ref") not in approval.get("target_refs", []): graph_fail.append("Effect approval target")

        evidence, verdict, method = by_type["evidence"]["payload"], by_type["criteria_verdict"]["payload"], by_type["validation_method"]["payload"]
        for ref in evidence.get("raw_observation_refs", []):
            if not (EXAMPLE/ref).is_file(): graph_fail.append(f"missing raw observation {ref}")
        if evidence.get("method_id") != method.get("method_id") or evidence.get("method_revision") != method.get("method_revision"): graph_fail.append("Evidence method identity")
        if evidence.get("claim_id") not in method.get("claim_ids", []): graph_fail.append("Evidence claim/method")
        if verdict.get("criterion_id") != evidence.get("criterion_id"): graph_fail.append("Verdict/Evidence criterion")
        if set(verdict.get("evidence_refs", [])) - set(pp.get("evidence_index_refs", [])): graph_fail.append("Verdict Evidence not indexed")
        if set(verdict.get("method_refs", [])) - set(plan.get("validation_method_refs", [])): graph_fail.append("Verdict method not in Plan")

        for ref_key in ["work_state_ref", "work_control_ref", "source_request_ref", "definition_ref", "execution_plan_ref", "active_blocker_set_ref", "budget_ref", "artifact_manifest_ref"]:
            ref_value = pp.get(ref_key)
            if ref_value is not None and not (EXAMPLE/ref_value.split("#",1)[0]).is_file(): graph_fail.append(f"missing projection ref {ref_key}")
    except Exception as exc:
        graph_fail.append(str(exc))
    add(out, "S-28", not graph_fail, "Canonical fixture forms one digest-bound, authority-consistent operational graph", f"Canonical graph failures: {graph_fail}")

    # End-to-end semantic trace: no source clause or MUST claim may disappear between P1, P2, and validation.
    trace_fail: list[str] = []
    try:
        src = front_matter(EXAMPLE/"records/SRC-0001.md")
        definition = front_matter(EXAMPLE/"records/DEF-0001.md")
        admission = front_matter(EXAMPLE/"records/ADM-0001.md")
        plan = front_matter(EXAMPLE/"records/PLAN-0001.md")
        method = front_matter(EXAMPLE/"records/VM-0001.md")
        sp, dp, ap, xp, mp = src["payload"], definition["payload"], admission["payload"], plan["payload"], method["payload"]
        source_ids = {f"{src['record_id']}:{item['item_id']}" for item in sp.get("source_items", [])}
        coverage = dp.get("coverage", [])
        coverage_ids = [c.get("source_item_ref") for c in coverage]
        if set(coverage_ids) != source_ids or len(coverage_ids) != len(set(coverage_ids)): trace_fail.append("source coverage is not exact")
        if dp.get("unresolved_items"): trace_fail.append("definition has unresolved items")
        req_source_ids = {ref for req in dp.get("requirements", []) for ref in req.get("source_item_refs", [])}
        if not req_source_ids.issubset(source_ids): trace_fail.append("requirement references unknown source")
        requirement_ids = {req.get("requirement_id") for req in dp.get("requirements", [])}
        for c in coverage:
            if c.get("disposition") in {"must", "should"} and c.get("target_ref") not in requirement_ids:
                trace_fail.append(f"coverage target missing {c.get('target_ref')}")
        must_claims = {claim for req in dp.get("requirements", []) if req.get("kind") == "must" for claim in req.get("acceptance_claim_ids", [])}
        plan_claims = set(xp.get("integration_claim_ids", [])) | {claim for unit in xp.get("units", []) for claim in unit.get("expected_claim_ids", [])}
        if not must_claims.issubset(set(mp.get("claim_ids", []))): trace_fail.append("MUST claim lacks Validation Method")
        if not must_claims.issubset(plan_claims): trace_fail.append("MUST claim lacks Plan coverage")
        if xp.get("definition_ref") != "records/DEF-0001.md": trace_fail.append("Plan uses stale Definition")
        if "records/VM-0001.md" not in xp.get("validation_method_refs", []): trace_fail.append("Plan lacks adopted Validation Method")
        unit_ids = [u.get("unit_id") for u in xp.get("units", [])]
        if len(unit_ids) != len(set(unit_ids)) or None in unit_ids: trace_fail.append("Plan Unit identity invalid")
        for unit in xp.get("units", []):
            for ref in unit.get("validation_hook_refs", []) + unit.get("effect_intent_refs", []):
                if not (EXAMPLE/ref).is_file(): trace_fail.append(f"missing Unit ref {ref}")
        for assumption in dp.get("assumptions", []):
            if assumption.get("status") == "needs_validation":
                route = assumption.get("validation_route_ref")
                if not route or not (EXAMPLE/route).is_file(): trace_fail.append(f"assumption has no valid route {assumption.get('assumption_id')}")
        fidelity = dp.get("fidelity_review", {})
        if fidelity.get("required") and (not fidelity.get("review_ref") or fidelity.get("adoption_status") != "adopted"):
            trace_fail.append("required fidelity review not adopted")
        if not fidelity.get("required") and fidelity.get("adoption_status") not in {"not_required", "adopted"}: trace_fail.append("invalid fidelity review disposition")
        if "records/SRC-0001.md" not in ap.get("source_request_refs", []) or dp.get("admission_ref") != "records/ADM-0001.md": trace_fail.append("Admission/Definition source chain")
        if xp.get("budget_allocation_ref") != "records/BUD-0001.md": trace_fail.append("Plan budget chain")
    except Exception as exc:
        trace_fail.append(str(exc))
    add(out, "S-29", not trace_fail, "Source→Definition→Plan→Validation traceability is exact for the canonical work", f"Traceability failures: {trace_fail}")

    # Core wording guards for the authority fixes found during second-pass review.
    core_guard_fail: list[str] = []
    p1_guard = (RUNTIME/"core/P1_作業定義ハーネス.md").read_text(encoding="utf-8")
    p2_guard = (RUNTIME/"core/P2_作業設計ハーネス.md").read_text(encoding="utf-8")
    p6_guard = (RUNTIME/"core/P6_終了・引き渡しハーネス.md").read_text(encoding="utf-8")
    if "Source→Definition coverage reviewを要求する" not in p1_guard: core_guard_fail.append("P1 fidelity review requirement")
    if "適用されるEffect recovery" not in p2_guard: core_guard_fail.append("P2 conditional Effect recovery")
    if "checkpointを直接後退させない" not in p6_guard or "Active Blocker" not in p6_guard: core_guard_fail.append("P6 settlement failure authority")
    add(out, "S-30", not core_guard_fail, "P1 fidelity, P2 conditional Effect recovery, and P6 settlement-failure authority guards are normative", f"Core authority guards missing: {core_guard_fail}")
    return out


# ---------- deterministic contract model ----------

def route_j1(checkpoint: str, interrupt_ref: str | None, *, lifecycle: str="active", pending_control: bool=False) -> str:
    if lifecycle != "active" or pending_control:
        return "NO_DISPATCH"
    if checkpoint not in ALLOWED_CHECKPOINTS:
        return "CONTROL_FAULT"
    if checkpoint == "closed":
        return "DONE" if interrupt_ref is None else "CONTROL_FAULT"
    if interrupt_ref is not None:
        return "P5"
    return {"none":"P1","defined":"P2","designed":"P3","executed":"P4","accepted":"P6"}[checkpoint]

WORK_TRANSITIONS={
    "active":{"suspended","canceling","terminated"},
    "suspended":{"active","canceling","terminated"},
    "canceling":{"terminated"},
    "terminated":{"archived"},
    "archived":set(),
}
OP_TRANSITIONS={
    "prepared":{"submitted","canceled"},
    "submitted":{"running","waiting_input","waiting_authorization","succeeded","failed","rejected","timed_out","canceled","unknown"},
    "running":{"waiting_input","waiting_authorization","succeeded","failed","rejected","timed_out","canceled","unknown"},
    "waiting_input":{"submitted","running","succeeded","failed","rejected","timed_out","canceled","unknown"},
    "waiting_authorization":{"submitted","running","succeeded","failed","rejected","timed_out","canceled","unknown"},
    "unknown":{"running","waiting_input","waiting_authorization","succeeded","failed","rejected","timed_out","canceled"},
    "succeeded":set(),"failed":set(),"rejected":set(),"timed_out":set(),"canceled":set(),
}

def transition(table: dict[str,set[str]], old: str, new: str) -> bool:
    return new in table.get(old,set())

def can_retry_operation(states: Iterable[str]) -> bool:
    return not any(s in {"submitted","running","waiting_input","waiting_authorization","unknown"} for s in states)

def return_adoptable(*, expected_refs:dict[str,str], current_refs:dict[str,str], actual_cap:str, expected_cap:str, sequence:int, last_sequence:int, schema_valid:bool=True) -> bool:
    return schema_valid and expected_refs==current_refs and actual_cap==expected_cap and sequence>last_sequence

def blocker_set_clearable(statuses:list[str]) -> bool:
    return bool(statuses) and all(s in {"resolved","superseded"} for s in statuses)

def should_suspend_for_waiting(statuses:list[str], *, global_gate:bool=False) -> bool:
    blocking=[s for s in statuses if s not in {"resolved","superseded"}]
    return global_gate or (bool(blocking) and all(s=="waiting" for s in blocking))

def p4_route(*, predefined:bool, unambiguous:bool, route:str) -> str:
    return route if predefined and unambiguous and route in {"none","defined","designed","executed"} else "ACTIVE_BLOCKER"

def p5_rollback(*, definition_invalid=False, design_invalid=False, target_invalid=False, evidence_only=False) -> str:
    if definition_invalid: return "none"
    if design_invalid: return "defined"
    if target_invalid: return "designed"
    if evidence_only: return "executed"
    return "designed"

def acceptance_allowed(criteria:list[dict[str,Any]]) -> bool:
    for c in criteria:
        if not c.get("must",True): continue
        if c.get("verdict")!="PASS" or c.get("stale") or c.get("conflict") or not c.get("coverage_complete",True): return False
        if c.get("requires_independent") and len(set(c.get("independence_groups",[])))<2: return False
    return True

def effect_start_allowed(state:str, *, design_allows=True, reconciled=True, approval=True, budget=True) -> bool:
    if not (design_allows and reconciled and approval and budget): return False
    return state in {"intended","failed","compensated"}

def closure_allowed(*, all_pass:bool, blockers:int, inflight:int, unsettled_effects:int, pending_control:int, handoff:bool) -> bool:
    return all_pass and blockers==0 and inflight==0 and unsettled_effects==0 and pending_control==0 and handoff

def terminal_consistent(*, lifecycle:str, disposition:str, checkpoint:str) -> bool:
    if lifecycle!="terminated": return False
    if disposition=="completed": return checkpoint=="closed"
    return checkpoint!="closed"

def admission_allowed(flags:dict[str,bool], risk_tier:str, *, t2_controls:bool=False) -> bool:
    if not all(flags.values()): return False
    if risk_tier in {"T0","T1"}: return True
    if risk_tier=="T2": return t2_controls
    return False

def definition_promotable(source_ids:set[str], coverage:list[dict[str,str]]) -> bool:
    dispositions={"must","should","design_discretion","out_of_scope","superseded_by_amendment"}
    seen=[c.get("source_item_ref") for c in coverage]
    return set(seen)==source_ids and len(seen)==len(set(seen)) and all(c.get("disposition") in dispositions for c in coverage)

def units_to_resume(units:list[dict[str,Any]], invalidated:set[str]) -> set[str]:
    out=set()
    for u in units:
        if u["unit_id"] in invalidated or u["state"] not in {"succeeded","skipped"}:
            out.add(u["unit_id"])
    return out

def recover_projection(*, commit_durable:bool, alias_points_new:bool) -> str:
    if commit_durable: return "REBUILD_NEW"
    if alias_points_new: return "REJECT_ALIAS_TO_PREVIOUS"
    return "USE_PREVIOUS"


def dispatch_binding_valid(*, packet_digest:str, adopted_digest:str, packet_identity:dict[str,str], operation_identity:dict[str,str]) -> bool:
    return packet_digest == adopted_digest and packet_identity == operation_identity


def projection_sources_agree(*, budget_source:dict[str,Any], budget_cache:dict[str,Any], unit_source:dict[str,Any], unit_cache:dict[str,Any]) -> bool:
    return budget_source == budget_cache and unit_source == unit_cache


def progress_adoptable(*, activity_only: bool, newly_adopted_refs: list[str], material_difference: str, net_material: bool) -> bool:
    return (not activity_only) and bool(newly_adopted_refs) and bool(material_difference.strip()) and net_material


def autonomy_may_continue(*, usage: dict[str, float], limits: dict[str, float], override: bool=False) -> bool:
    if override:
        return True
    return all(float(usage.get(key, 0)) < float(limit) for key, limit in limits.items())


def execution_promotable(*, provider_success: bool, required_units_adopted: bool, inflight_operations: int, unknown_effects: int) -> bool:
    # Provider success is an observation, not P3 adoption or proof of Effect settlement.
    return provider_success and required_units_adopted and inflight_operations == 0 and unknown_effects == 0


def return_digest_adoptable(*, return_ref: str | None, expected_digest: str | None, actual_digest: str | None) -> bool:
    return bool(return_ref) and bool(expected_digest) and expected_digest == actual_digest


def settlement_failure_route(*, prerequisites_satisfied: bool, predefined_validation_route: bool=False) -> str:
    if prerequisites_satisfied:
        return "CLOSE"
    return "P4_PREDEFINED_ROUTE" if predefined_validation_route else "ACTIVE_BLOCKER"


def model_cases() -> list[dict[str,str]]:
    flags={"finite":True,"criteria":True,"effects":True,"observable":True,"single_checkpoint":True,"context":True,"capability":True}
    cases:list[tuple[str,Callable[[],bool],str]]=[
        ("M-01",lambda:[route_j1(c,None) for c in ALLOWED_CHECKPOINTS]==["P1","P2","P3","P4","P6","DONE"],"J1 six-checkpoint routing"),
        ("M-02",lambda:route_j1("designed",None,lifecycle="suspended")=="NO_DISPATCH","Suspended Work Control blocks J1"),
        ("M-03",lambda:route_j1("defined","BLKSET-1")=="P5","Active blocker routes P5"),
        ("M-04",lambda:route_j1("designed",None,pending_control=True)=="NO_DISPATCH","Pending cancel/amendment blocks J1"),
        ("M-05",lambda:route_j1("WAIT",None)=="CONTROL_FAULT","Unknown Achievement state fails closed"),
        ("M-06",lambda:transition(WORK_TRANSITIONS,"active","suspended") and transition(WORK_TRANSITIONS,"suspended","active"),"Pause/resume lifecycle"),
        ("M-07",lambda:transition(WORK_TRANSITIONS,"active","canceling") and transition(WORK_TRANSITIONS,"canceling","terminated"),"Finite cancel lifecycle"),
        ("M-08",lambda:not transition(WORK_TRANSITIONS,"terminated","active"),"Terminal work cannot silently resume"),
        ("M-09",lambda:transition(OP_TRANSITIONS,"submitted","succeeded"),"Immediate provider success is legal"),
        ("M-10",lambda:transition(OP_TRANSITIONS,"running","unknown") and transition(OP_TRANSITIONS,"unknown","timed_out"),"Unknown Operation reconciles to observed terminal"),
        ("M-11",lambda:not transition(OP_TRANSITIONS,"succeeded","running"),"Terminal Operation cannot restart"),
        ("M-12",lambda:not can_retry_operation(["unknown"]),"Unknown Operation prevents duplicate retry"),
        ("M-13",lambda:return_adoptable(expected_refs={"plan":"P2"},current_refs={"plan":"P2"},actual_cap="cap@1",expected_cap="cap@1",sequence=2,last_sequence=1),"Current ordered Return is adoptable"),
        ("M-14",lambda:not return_adoptable(expected_refs={"plan":"P1"},current_refs={"plan":"P2"},actual_cap="cap@1",expected_cap="cap@1",sequence=2,last_sequence=1),"Stale Return is rejected"),
        ("M-15",lambda:not return_adoptable(expected_refs={"plan":"P2"},current_refs={"plan":"P2"},actual_cap="cap@2",expected_cap="cap@1",sequence=2,last_sequence=1),"Capability revision drift is rejected"),
        ("M-16",lambda:not return_adoptable(expected_refs={"plan":"P2"},current_refs={"plan":"P2"},actual_cap="cap@1",expected_cap="cap@1",sequence=1,last_sequence=1),"Duplicate/out-of-order Return is rejected"),
        ("M-17",lambda:not blocker_set_clearable(["resolved","waiting"]),"Partial blocker resolution keeps set open"),
        ("M-18",lambda:blocker_set_clearable(["resolved","superseded"]),"All blockers resolved/superseded clear set"),
        ("M-19",lambda:not should_suspend_for_waiting(["waiting","investigating"]),"One waiting blocker does not freeze other diagnosable blockers"),
        ("M-20",lambda:should_suspend_for_waiting(["waiting","waiting"]),"All blocking work waiting causes suspend"),
        ("M-21",lambda:p4_route(predefined=True,unambiguous=True,route="defined")=="defined","P4 may apply predefined validation route"),
        ("M-22",lambda:p4_route(predefined=False,unambiguous=True,route="defined")=="ACTIVE_BLOCKER","P4 cannot invent rollback route"),
        ("M-23",lambda:p5_rollback(target_invalid=True)=="designed","Target mutation returns to P3 authority"),
        ("M-24",lambda:p5_rollback(design_invalid=True)=="defined","Design mutation returns to P2 authority"),
        ("M-25",lambda:p5_rollback(definition_invalid=True)=="none","Definition invalidation returns to P1 authority"),
        ("M-26",lambda:p5_rollback(evidence_only=True)=="executed","Evidence-only recovery may retain executed"),
        ("M-27",lambda:not acceptance_allowed([{"must":True,"verdict":"UNKNOWN"}]),"UNKNOWN criterion prevents Acceptance"),
        ("M-28",lambda:not acceptance_allowed([{"must":True,"verdict":"PASS","conflict":True}]),"Contradictory Evidence prevents Acceptance"),
        ("M-29",lambda:not acceptance_allowed([{"must":True,"verdict":"PASS","stale":True}]),"Stale Evidence prevents Acceptance"),
        ("M-30",lambda:not acceptance_allowed([{"must":True,"verdict":"PASS","coverage_complete":False}]),"Partial coverage prevents Acceptance"),
        ("M-31",lambda:not acceptance_allowed([{"must":True,"verdict":"PASS","requires_independent":True,"independence_groups":["shared"]}]),"Correlated-only Evidence is not an independent check"),
        ("M-32",lambda:acceptance_allowed([{"must":True,"verdict":"PASS","requires_independent":True,"independence_groups":["g1","g2"]}]),"Current independent Evidence can pass"),
        ("M-33",lambda:not effect_start_allowed("unknown"),"Unknown Effect prevents retry"),
        ("M-34",lambda:not effect_start_allowed("confirmed"),"Confirmed Effect is not duplicated"),
        ("M-35",lambda:effect_start_allowed("compensated"),"Compensated Effect may permit a new attempt"),
        ("M-36",lambda:recover_projection(commit_durable=False,alias_points_new=False)=="USE_PREVIOUS","Crash before Commit ignores staging"),
        ("M-37",lambda:recover_projection(commit_durable=True,alias_points_new=False)=="REBUILD_NEW","Commit before alias update rebuilds new projection"),
        ("M-38",lambda:recover_projection(commit_durable=False,alias_points_new=True)=="REJECT_ALIAS_TO_PREVIOUS","Uncommitted alias is rejected"),
        ("M-39",lambda:not closure_allowed(all_pass=True,blockers=0,inflight=1,unsettled_effects=0,pending_control=0,handoff=True),"Inflight Operation blocks closure"),
        ("M-40",lambda:not closure_allowed(all_pass=True,blockers=0,inflight=0,unsettled_effects=1,pending_control=0,handoff=True),"Unsettled Effect blocks closure"),
        ("M-41",lambda:closure_allowed(all_pass=True,blockers=0,inflight=0,unsettled_effects=0,pending_control=0,handoff=True),"Completion settlement can close"),
        ("M-42",lambda:terminal_consistent(lifecycle="terminated",disposition="completed",checkpoint="closed"),"Successful terminal aligns closed/completed"),
        ("M-43",lambda:terminal_consistent(lifecycle="terminated",disposition="canceled",checkpoint="designed"),"Canceled terminal preserves last valid Achievement"),
        ("M-44",lambda:not terminal_consistent(lifecycle="terminated",disposition="canceled",checkpoint="closed"),"Non-success terminal cannot claim closed"),
        ("M-45",lambda:admission_allowed(flags,"T1"),"Bounded T1 digital work is admissible"),
        ("M-46",lambda:not admission_allowed(flags,"T2",t2_controls=False),"T2 requires explicit controls"),
        ("M-47",lambda:admission_allowed(flags,"T2",t2_controls=True),"Controlled T2 may be admitted within scope"),
        ("M-48",lambda:not admission_allowed(flags,"T3",t2_controls=True),"T3 is outside autonomous P3 scope"),
        ("M-49",lambda:not admission_allowed({**flags,"finite":False},"T1"),"Open-ended monitoring is rejected/split"),
        ("M-50",lambda:definition_promotable({"S1","S2"},[{"source_item_ref":"S1","disposition":"must"},{"source_item_ref":"S2","disposition":"design_discretion"}]),"Complete source coverage can promote Definition"),
        ("M-51",lambda:not definition_promotable({"S1","S2"},[{"source_item_ref":"S1","disposition":"must"}]),"Dropped source clause prevents defined"),
        ("M-52",lambda:not definition_promotable({"S1"},[{"source_item_ref":"S1","disposition":"unresolved_blocker"}]),"Unresolved blocker prevents defined"),
        ("M-53",lambda:units_to_resume([{"unit_id":"U1","state":"succeeded"},{"unit_id":"U2","state":"blocked"}],set())=={"U2"},"Resume only unfinished units"),
        ("M-54",lambda:units_to_resume([{"unit_id":"U1","state":"succeeded"},{"unit_id":"U2","state":"succeeded"}],{"U1"})=={"U1"},"Dependency invalidation reruns only affected unit"),
        ("M-55",lambda:dispatch_binding_valid(packet_digest="abc",adopted_digest="abc",packet_identity={"dispatch_id":"D1","attempt_id":"A1"},operation_identity={"dispatch_id":"D1","attempt_id":"A1"}),"Exact Dispatch digest and identity binding is accepted"),
        ("M-56",lambda:not dispatch_binding_valid(packet_digest="abc",adopted_digest="def",packet_identity={"dispatch_id":"D1"},operation_identity={"dispatch_id":"D1"}),"Mutated Dispatch digest is rejected"),
        ("M-57",lambda:projection_sources_agree(budget_source={"usage":1},budget_cache={"usage":1},unit_source={"state":"blocked"},unit_cache={"state":"blocked"}),"Immutable Budget/Unit sources can agree with current projection caches"),
        ("M-58",lambda:not projection_sources_agree(budget_source={"usage":1},budget_cache={"usage":2},unit_source={"state":"blocked"},unit_cache={"state":"running"}),"Projection/source drift is rejected"),
        ("M-59",lambda:not progress_adoptable(activity_only=True,newly_adopted_refs=[],material_difference="renamed strategy only",net_material=False),"Activity or strategy churn alone is not Progress"),
        ("M-60",lambda:progress_adoptable(activity_only=False,newly_adopted_refs=["EVD-2"],material_difference="cause candidates reduced",net_material=True),"Adopted material net improvement is Progress"),
        ("M-61",lambda:not autonomy_may_continue(usage={"attempts":3,"tool_calls":4},limits={"attempts":3,"tool_calls":20}),"Hard autonomy budget stops further execution"),
        ("M-62",lambda:not execution_promotable(provider_success=True,required_units_adopted=False,inflight_operations=0,unknown_effects=0),"Provider success without P3 adoption cannot promote executed"),
        ("M-63",lambda:not return_digest_adoptable(return_ref="RET-1",expected_digest="abc",actual_digest="def"),"Capability Return digest mismatch prevents adoption"),
        ("M-64",lambda:settlement_failure_route(prerequisites_satisfied=False)=="ACTIVE_BLOCKER","P6 settlement failure routes through Active Blocker rather than direct rollback"),
    ]
    result=[]
    for cid,fn,detail in cases:
        try:
            ok=bool(fn())
            result.append({"case_id":cid,"status":"PASS" if ok else "FAIL","detail":detail})
        except Exception as exc:
            result.append({"case_id":cid,"status":"FAIL","detail":f"{detail}: {exc}"})
    return result


def write_reports(static:list[Check], model:list[dict[str,str]]) -> None:
    static_fail=[c for c in static if c.status=="FAIL"]
    model_fail=[c for c in model if c["status"]=="FAIL"]
    overall="PASS" if not static_fail and not model_fail else "FAIL"
    report={
        "artifact":"Fluid Progress Orchestration v0.2 Architectural Hardening Candidate",
        "scope":"static bundle integrity + JSON Schema/canonical fixture + deterministic contract model",
        "overall_status":overall,"runtime_e2e":"NOT_EXECUTED",
        "static_summary":{"pass":sum(c.status=="PASS" for c in static),"fail":len(static_fail),"skip":sum(c.status=="SKIP" for c in static)},
        "model_summary":{"pass":len(model)-len(model_fail),"fail":len(model_fail)},
        "model_cases":model,
        "limitations":[
            "No LLM/Agent behavior executed", "No real filesystem crash/fsync/lock implementation tested",
            "No external side effect or adversarial prompt injection executed", "No repeated sandbox E2E performed",
        ],
    }
    (VALIDATION/"MODEL_CHECK_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# FPO v0.2 Static Integrity Check","",f"## Status: **{overall}**","",
           "This proves static identity, schema/fixture consistency, and deterministic invariants only. Runtime behavior remains unproven until sandbox E2E.","",
           "## Static checks","","| ID | Status | Detail |","|---|---|---|"]
    for c in static: lines.append(f"| {c.check_id} | {c.status} | {c.detail.replace('|','/')} |")
    lines += ["","## Deterministic model","","| ID | Status | Invariant |","|---|---|---|"]
    for c in model: lines.append(f"| {c['case_id']} | {c['status']} | {c['detail'].replace('|','/')} |")
    lines += ["","## Explicitly not proven","","- autonomous completion quality","- root-cause accuracy on long LLM traces",
              "- real crash durability and concurrency","- prompt-injection resistance","- repeated E2E reliability/cost","- non-software generality"]
    (VALIDATION/"STATIC_INTEGRITY_CHECK.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def main() -> int:
    static=static_checks(); model=model_cases(); write_reports(static,model)
    failures=[c for c in static if c.status=="FAIL"]+[c for c in model if c["status"]=="FAIL"]
    print(json.dumps({
        "overall":"PASS" if not failures else "FAIL",
        "static":{"pass":sum(c.status=="PASS" for c in static),"fail":sum(c.status=="FAIL" for c in static),"skip":sum(c.status=="SKIP" for c in static)},
        "model":{"pass":sum(c["status"]=="PASS" for c in model),"fail":sum(c["status"]=="FAIL" for c in model)},
        "failures":[c.detail if isinstance(c,Check) else c.get("detail","") for c in failures],
    },ensure_ascii=False,indent=2))
    return 1 if failures else 0

if __name__=="__main__":
    sys.exit(main())
