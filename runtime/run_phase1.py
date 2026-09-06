#!/usr/bin/env python3
"""Deterministic Phase 1 crash-durability probe.

Each case owns an independent FPO run directory and an independent mutable
provider journal.  The journal represents provider-side truth only; FPO
control state remains immutable records plus the CAS commit chain.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from run_baseline import (
    BINDING_REF,
    BUNDLE_ID,
    CAPABILITY_ID,
    CAPABILITY_REVISION,
    DESIGN_REVISION,
    DISPATCH_ID,
    INPUT_PATH,
    LOGICAL_INTENT_ID,
    OPERATION_ID,
    OUTPUT_PATH,
    PLAN_UNIT_ID,
    POLICY_REVISION,
    RUNNER_ROOT,
    SCHEMA_PATH,
    SPEC_RUNTIME_ROOT,
    TARGET_REVISION,
    WORK_ID,
    JsonSchemaValidator,
    OperationController,
    ProbeError,
    RunStore,
    actor,
    append_record,
    base_payloads,
    effect_payload,
    enforce_phase0_effect_boundary,
    json_bytes,
    make_dispatch,
    make_return,
    operation_payload,
    read_frontmatter,
    run_worker,
    sha256_file,
    unit_state_payload,
    utc_now,
    validate_manifest,
    verify_run,
    write_bytes,
)


EXIT_CRASH = 86
CASES = {
    "C1": "after_dispatch_commit_before_capability_submit",
    "C2": "after_provider_submit_before_remote_id_persist",
    "C3": "operation_running",
    "C4": "after_immutable_return_before_p3_adoption",
}
EXPECTED = json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8"))
FINDING_CLASSIFICATION = {
    "category": "Runtime integration defect",
    "summary": "SPEC_RUNTIME_ROOTとRUNNER_ROOTの取り違え。Phase 0のhash-only fallbackがこれを隠していた。",
}


def relative_run(path: Path) -> str:
    return path.relative_to(RUNNER_ROOT).as_posix()


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, json_bytes(value))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProbeError(f"expected JSON object: {path}")
    return value


def hydrate_store(run_dir: Path) -> RunStore:
    """Re-open an existing immutable run without inventing missing control state."""
    if not (run_dir / "head.json").is_file():
        raise ProbeError(f"run has no durable head: {run_dir}")
    store = object.__new__(RunStore)
    store.run_dir = run_dir
    store.bundle_revision = validate_manifest()["bundle_revision"]
    store.run_time = utc_now()
    store.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    store.validator = JsonSchemaValidator(store.schema)
    store.sequence = 0
    store.state_revision = 0
    store.current_commit_id = None
    store.refs = []
    store.record_values = {}
    store.commit_refs = []
    store.log_path = run_dir / "run.log"

    all_frontmatter = sorted(run_dir.rglob("*.md"))
    for path in all_frontmatter:
        value = read_frontmatter(path)
        store.sequence = max(store.sequence, int(value.get("sequence", 0)))
        ref = path.relative_to(run_dir).as_posix()
        store.refs.append(ref)
        if value.get("schema_name") == "fpo.record":
            store.validator.validate(value, store.schema)
            store.record_values[ref] = value
        if path.parent.name == "commits":
            store.commit_refs.append(ref)
    commits = sorted(
        ((read_frontmatter(path)["payload"]["new_state_revision"], path, read_frontmatter(path))
         for path in (run_dir / "commits").glob("COM-*.md")),
        key=lambda item: item[0],
    )
    if not commits:
        raise ProbeError("run has no immutable commit")
    store.state_revision = commits[-1][0]
    store.current_commit_id = commits[-1][2]["payload"]["commit_id"]
    return store


def latest(store: RunStore, record_type: str, logical_id: str) -> dict[str, Any]:
    value = store.latest_record(record_type, logical_id)
    if value is None:
        raise ProbeError(f"missing latest {record_type}/{logical_id}")
    return value


def latest_ref(store: RunStore, record_type: str, logical_id: str) -> str:
    value = latest(store, record_type, logical_id)
    for ref, candidate in store.record_values.items():
        if candidate is value:
            return ref
    raise ProbeError(f"missing ref for {record_type}/{logical_id}")


def next_record_id(store: RunStore, prefix: str) -> str:
    numbers = []
    for path in (store.run_dir / "records").glob(f"{prefix}-*.md"):
        try:
            numbers.append(int(path.stem.rsplit("-", 1)[-1]))
        except ValueError:
            pass
    return f"{prefix}-{(max(numbers) + 1 if numbers else 1):04d}"


def build_prefix(run_dir: Path, case_id: str) -> dict[str, Any]:
    manifest = validate_manifest()
    if OUTPUT_PATH.exists():
        raise ProbeError("Phase 1 fresh case requires output to be absent")
    if INPUT_PATH.read_text(encoding="utf-8") != EXPECTED["input_text"]:
        raise ProbeError("canonical input does not match probe fixture")

    store = RunStore(run_dir, manifest["bundle_revision"], utc_now())
    store.log("runtime_start", phase="phase1", case_id=case_id, manifest=manifest, crash_point=CASES[case_id])
    input_ref = "workspace/input.txt"
    output_ref = "workspace/output/output.txt"
    payloads = base_payloads(input_ref, output_ref)
    payloads["budget"]["measured_at"] = store.run_time
    payloads["approval"]["valid_from"] = store.run_time

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
        "lifecycle_state": "active", "terminal_disposition": None, "reason": "Phase 1 crash durability case is active.",
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
    op_prepared = append_record(store, "delegated_operation", "OP-0001", "OP-INT-001", operation_payload(dispatch_sha, "prepared", effect_refs=[effect_intended], remote_operation_id=None), actor("runtime-1", "runtime", "operation_lifecycle"))
    commit_ref = store.commit([effect_intended, unit_pending, packet_ref, op_prepared], op_prepared, "Dispatch packet and prepared operation committed with digest binding.")
    store.log("crash_ready", case_id=case_id, crash_point=CASES[case_id], last_commit_before_crash=Path(commit_ref).stem)
    crash = {"case_id": case_id, "crash_point": CASES[case_id], "initial_run_id": f"{case_id}-initial-{store.run_time}", "last_commit_before_crash": Path(commit_ref).stem, "exit_code": EXIT_CRASH}
    write_json(run_dir / "crash.json", crash)
    write_json(run_dir / "phase1_metrics.json", {"case_id": case_id, "initial_run_id": crash["initial_run_id"], "recovery_run_id": None, "crash_point": crash["crash_point"], "last_commit_before_crash": crash["last_commit_before_crash"]})
    return {"store": store, "packet": packet, "packet_ref": packet_ref, "dispatch_sha": dispatch_sha, "effect_ref": effect_intended, "op_ref": op_prepared, "crash": crash}


def provider_path(run_dir: Path) -> Path:
    return run_dir / "provider_journal" / "provider.json"


def provider_submit(run_dir: Path, dispatch_sha: str, store: RunStore) -> dict[str, Any]:
    path = provider_path(run_dir)
    if path.exists():
        journal = load_json(path)
        if journal["dispatch_digest"] != dispatch_sha or journal["idempotency_key"] != f"{WORK_ID}:{LOGICAL_INTENT_ID}:output-v1":
            raise ProbeError("provider idempotency identity mismatch")
        store.log("provider_submit_reused", operation_id=journal["operation_id"], invocation_count=journal["invocation_count"], state=journal["state"])
        return journal
    journal = {
        "work_id": WORK_ID, "dispatch_id": DISPATCH_ID, "dispatch_digest": dispatch_sha, "logical_intent_id": LOGICAL_INTENT_ID,
        "idempotency_key": f"{WORK_ID}:{LOGICAL_INTENT_ID}:output-v1", "operation_id": OPERATION_ID,
        "invocation_count": 1, "effect_count": 0, "started_at": utc_now(), "completed_at": None,
        "state": "submitted", "remote_operation_id": OPERATION_ID, "return_ref": None, "return_sha256": None,
        "reconcile_count": 0,
    }
    write_json(path, journal)
    store.log("provider_submit", operation_id=OPERATION_ID, invocation_count=1, idempotency_key=journal["idempotency_key"], dispatch_sha256=dispatch_sha)
    return journal


def provider_set_running(run_dir: Path, store: RunStore) -> dict[str, Any]:
    journal = load_json(provider_path(run_dir))
    if journal["state"] == "completed":
        return journal
    journal["state"] = "running"
    write_json(provider_path(run_dir), journal)
    store.log("provider_running", operation_id=journal["operation_id"])
    return journal


def persist_running(store: RunStore, dispatch_sha: str, effect_intended_ref: str) -> tuple[str, str]:
    current = latest(store, "delegated_operation", "OP-INT-001")
    if current["payload"]["state"] in {"running", "succeeded"}:
        return latest_ref(store, "delegated_operation", "OP-INT-001"), latest_ref(store, "effect", "EFF-INT-001")
    submitted = append_record(store, "delegated_operation", "OP-0002", "OP-INT-001", operation_payload(dispatch_sha, "submitted", effect_refs=[effect_intended_ref], provider_sequence=1, remote_operation_id=OPERATION_ID), actor("runtime-1", "runtime", "operation_lifecycle"), revision=2)
    store.commit([submitted], submitted, "Recovered provider submission and persisted remote operation identity.")
    started = append_record(store, "effect", "EFF-0002", "EFF-INT-001", effect_payload("started"), actor("runtime-1", "runtime", "effect_lifecycle_projection"), revision=2)
    unit_running = append_record(store, "plan_unit_state", "UNITSTATE-0003", "UNITSTATE-W-PHASE0-UNIT-001", unit_state_payload("running", operation_ref=submitted, effect_ref=started, last_event_ref=started), actor("runtime-1", "runtime", "execution_projection"), revision=3)
    running = append_record(store, "delegated_operation", "OP-0003", "OP-INT-001", operation_payload(dispatch_sha, "running", effect_refs=[started], provider_sequence=1, remote_operation_id=OPERATION_ID), actor("runtime-1", "runtime", "operation_lifecycle"), revision=3)
    store.commit([started, unit_running, running], running, "Recovered operation running state from provider observation.")
    return running, started


def provider_complete(run_dir: Path, store: RunStore, packet: dict[str, Any], effect_ref: str) -> dict[str, Any]:
    journal = load_json(provider_path(run_dir))
    if journal["dispatch_digest"] != sha256_file(store.ref_path(f"packets/{DISPATCH_ID}.md")):
        raise ProbeError("provider journal is not bound to the committed dispatch")
    if journal["state"] != "completed":
        if journal["effect_count"] != 0 or OUTPUT_PATH.exists():
            raise ProbeError("provider state is incomplete but effect/output already exists")
        worker_result, observation_ref = run_worker(packet, effect_payload("started"), store)
        journal["effect_count"] = 1
        journal["state"] = "completed"
        journal["completed_at"] = utc_now()
        journal["return_ref"] = "inbox/untrusted/RET-0001.md"
        journal["return_sha256"] = None
        write_json(provider_path(run_dir), journal)
    else:
        if journal["effect_count"] != 1 or not OUTPUT_PATH.exists():
            raise ProbeError("provider journal says completed without a durable effect")
        observation_ref = "observations/OBS-BASELINE.json"
        if not (store.run_dir / observation_ref).is_file():
            raise ProbeError("completed provider has no immutable observation")
        worker_result = {"status": "completed", "output_sha256": sha256_file(OUTPUT_PATH)}

    return_path = store.run_dir / "inbox" / "untrusted" / "RET-0001.md"
    if return_path.exists():
        return_ref = "inbox/untrusted/RET-0001.md"
        return_sha = sha256_file(return_path)
    else:
        return_message = make_return(packet, worker_result, store.run_time)
        return_ref = store.add_message(return_message, "inbox/untrusted", "RET-0001.md", "Untrusted capability Return; schema-valid but not control state.")
        return_sha = sha256_file(store.ref_path(return_ref))
    journal["return_ref"] = return_ref
    journal["return_sha256"] = return_sha
    write_json(provider_path(run_dir), journal)

    if latest(store, "delegated_operation", "OP-INT-001")["payload"]["state"] != "succeeded":
        op_succeeded = append_record(store, "delegated_operation", "OP-0004", "OP-INT-001", operation_payload(sha256_file(store.ref_path(f"packets/{DISPATCH_ID}.md")), "succeeded", return_ref=return_ref, return_sha=return_sha, effect_refs=[effect_ref], provider_sequence=2, remote_operation_id=OPERATION_ID), actor("runtime-1", "runtime", "operation_lifecycle"), revision=4)
        store.log("return_received", return_ref=return_ref, return_sha256=return_sha, dispatch_ref=f"packets/{DISPATCH_ID}.md", dispatch_sha256=sha256_file(store.ref_path(f"packets/{DISPATCH_ID}.md")), operation_ref=op_succeeded)
        store.commit([observation_ref, return_ref, op_succeeded], op_succeeded, "Return stored immutably after provider reconciliation; adoption remains pending.")
    return {"journal": journal, "observation_ref": observation_ref, "return_ref": return_ref, "return_sha": return_sha}


def adopt_and_close(store: RunStore, packet: dict[str, Any], dispatch_sha: str, method_ref: str, plan_ref: str, definition_ref: str, payloads: dict[str, Any], observation_ref: str, return_ref: str, return_sha: str) -> None:
    current_op = latest(store, "delegated_operation", "OP-INT-001")
    if current_op["payload"]["adoption_status"] != "adopted":
        output_sha = sha256_file(OUTPUT_PATH)
        artifact_ref = append_record(store, "artifact_manifest", "ART-0001", "ART-W-PHASE0", {
            "manifest_id": "ART-W-PHASE0-R1", "target_revision": TARGET_REVISION,
            "artifacts": [{"artifact_id": "ARTIFACT-001", "path_or_uri": "workspace/output/output.txt", "sha256": output_sha, "media_type": "text/plain", "revision": TARGET_REVISION, "source_unit_refs": [PLAN_UNIT_ID], "adoption_status": "adopted"}],
            "integration_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"], "environment_revision_refs": ["ENV-LOCAL-R1"],
        }, actor("p3-owner", "P3", "target_mutation"))
        confirmed = append_record(store, "effect", "EFF-0003", "EFF-INT-001", effect_payload("confirmed", output_sha, observation_ref), actor("p3-owner", "P3", "execution_adoption"), revision=3)
        unit_succeeded = append_record(store, "plan_unit_state", "UNITSTATE-0004", "UNITSTATE-W-PHASE0-UNIT-001", unit_state_payload("succeeded", operation_ref="records/OP-0005.md", effect_ref=confirmed, result_refs=[artifact_ref, observation_ref], last_event_ref=artifact_ref), actor("p3-owner", "P3", "execution_adoption"), revision=4)
        adopted = append_record(store, "delegated_operation", "OP-0005", "OP-INT-001", operation_payload(dispatch_sha, "succeeded", return_ref=return_ref, return_sha=return_sha, adoption="adopted", provider_sequence=2, evidence_refs=[observation_ref], effect_refs=[confirmed], remote_operation_id=OPERATION_ID), actor("p3-owner", "P3", "execution_adoption"), revision=5)
        ws_executed = append_record(store, "work_state", "WS-0004", "WS-W-PHASE0", {"checkpoint": "executed", "interrupt_ref": None}, actor("p3-owner", "P3", "execution_adoption"), revision=4)
        store.log("p3_adoption", operation_ref=adopted, effect_ref=confirmed, artifact_ref=artifact_ref, adoption_count=1)
        store.commit([artifact_ref, confirmed, unit_succeeded, adopted, ws_executed], ws_executed, "P3 adopted the reconciled artifact/effect exactly once; checkpoint executed.")
    else:
        artifact_ref = latest_ref(store, "artifact_manifest", "ART-W-PHASE0")

    if latest(store, "work_state", "WS-W-PHASE0")["payload"]["checkpoint"] == "executed":
        evidence_refs: list[str] = []
        verdict_refs: list[str] = []
        criteria = [
            ("A1", "CLM-A1", "workspace/input.txt", "Input SHA-256 remained unchanged from pre-dispatch observation."),
            ("A2", "CLM-A2", "workspace/output/output.txt", "Output exists at the separate target path."),
            ("A3", "CLM-A3", "workspace/output/output.txt", "Output bytes exactly match the expected uppercase fixture."),
            ("A4", "CLM-A4", "run.log", "Exactly one provider invocation and one effect were observed."),
            ("A5", "CLM-A5", "commits/", "Evidence/verdict records are committed before acceptance and closure."),
            ("A6", "CLM-A6", "records/OP-0005.md", "Final operation and effect are known terminal states; no unknown is adopted."),
            ("A7", "CLM-A7", "records/OP-0005.md", "P3 adoption is separate from the capability Return."),
        ]
        for index, (criterion_id, claim_id, object_ref, rationale) in enumerate(criteria, start=1):
            evidence_refs.append(append_record(store, "evidence", f"EVD-{index:04d}", f"EVD-{claim_id}", {
                "claim_id": claim_id, "criterion_id": criterion_id, "method_id": "filesystem.inspect", "method_revision": "1", "object_ref": object_ref, "object_revision": f"RUN-{store.run_time}", "design_revision": DESIGN_REVISION, "plan_revision": DESIGN_REVISION, "environment_ref": "ENV-LOCAL", "environment_revision": "ENV-LOCAL-R1", "observed_at": store.run_time, "freshness_policy": "Valid only for this fresh Phase 1 run.", "expires_at": None, "producer_id": "runtime-validator", "verifier_id": "p4-owner", "trust_domain": "local-readonly-probe", "source_lineage": [observation_ref, "probe/ACCEPTANCE.md"], "coverage": "full", "independence_basis": "Read-only runtime check separated from capability Return control authority.", "independence_group": "phase1-local-checks", "status": "valid", "supersedes_refs": [], "contradiction_refs": [], "raw_observation_refs": [observation_ref], "adopted_by": "P4",
            }, actor("p4-owner", "P4", "evidence_adoption"), explanation="P4-adopted machine evidence for the crash-durability criterion."))
            verdict_refs.append(append_record(store, "criteria_verdict", f"VER-{index:04d}", f"VER-{criterion_id}", {
                "criterion_id": criterion_id, "verdict": "PASS", "evidence_refs": [evidence_refs[-1]], "method_refs": [method_ref], "object_revision_refs": [TARGET_REVISION, f"RUN-{store.run_time}"], "coverage_complete": True, "freshness_ok": True, "conflict_status": "none", "independence_satisfied": True, "rationale": rationale,
            }, actor("p4-owner", "P4", "criteria_verdict"), explanation="P4 criterion verdict; capability self-report is not sufficient."))
        ws_accepted = append_record(store, "work_state", "WS-0005", "WS-W-PHASE0", {"checkpoint": "accepted", "interrupt_ref": None}, actor("p4-owner", "P4", "acceptance"), revision=5)
        store.commit(evidence_refs + verdict_refs + [ws_accepted], ws_accepted, "P4 adopted independent machine evidence and PASS verdicts; checkpoint accepted.")
    else:
        verdict_refs = [ref for ref, _ in store.latest_records_of_type("criteria_verdict")]

    if latest(store, "work_state", "WS-W-PHASE0")["payload"]["checkpoint"] == "accepted":
        budget_final = dict(payloads["budget"])
        budget_final["budget"] = dict(payloads["budget"]["budget"])
        budget_final["budget"]["usage"] = dict(payloads["budget"]["budget"]["usage"])
        budget_final["budget"]["usage"].update({"attempts": 1, "strategy_families": 1, "capability_calls": 1, "effect_count": 1})
        budget_final["measured_at"] = store.run_time
        budget_ref_final = append_record(store, "resource_budget", "BUD-0002", "BUD-W-PHASE0", budget_final, actor("runtime-1", "runtime", "work_control_projection"), revision=2)
        settlement_ref = append_record(store, "terminal_settlement", "SET-0001", "SET-W-PHASE0", {
            "disposition": "completed", "achievement_checkpoint": "closed", "definition_ref": definition_ref, "execution_plan_ref": plan_ref, "artifact_manifest_ref": artifact_ref, "criteria_verdict_refs": verdict_refs, "open_blocker_refs": [], "inflight_operation_refs": [], "unsettled_effect_refs": [], "known_limitations": ["Phase 1 uses deterministic crash cut points only."], "remaining_obligations": [], "handoff_ref": None, "retention_summary": "Phase 1 audit artifacts retained under this run directory.", "settled_at": store.run_time,
        }, actor("p6-owner", "P6", "successful_closure"), explanation="P6 successful closure settlement; no open operation/effect/blocker remains.")
        closure_event = append_record(store, "ledger_event", "EVT-0001", "EVT-W-PHASE0-CLOSURE", {"event_type": "closure", "summary": "Phase 1 crash-durability case reached completed terminal settlement.", "fact_refs": [settlement_ref, *verdict_refs], "decision_refs": [settlement_ref], "supersedes_refs": [], "rationale": "All recovery, adoption, evidence, and closure conditions are committed.", "hidden_reasoning_included": False}, actor("p6-owner", "P6", "successful_closure"))
        wc_closed = append_record(store, "work_control", "WC-0002", "WC-W-PHASE0", {"lifecycle_state": "terminated", "terminal_disposition": "completed", "reason": "P6 completed terminal settlement.", "resume_condition_ref": None, "resume_owner": None, "resume_expiry": None, "resume_default_action": None, "resume_default_action": None, "latest_user_event_ref": None, "active_approval_refs": [], "active_operation_refs": [], "unresolved_effect_refs": [], "autonomy_budget": budget_final["budget"]}, actor("runtime-1", "runtime", "work_control_projection"), revision=2)
        ws_closed = append_record(store, "work_state", "WS-0006", "WS-W-PHASE0", {"checkpoint": "closed", "interrupt_ref": None}, actor("p6-owner", "P6", "successful_closure"), revision=6)
        store.commit([budget_ref_final, settlement_ref, closure_event, wc_closed, ws_closed], settlement_ref, "P6 closure settlement; checkpoint closed and Work Control terminal/completed.")


def crash_start(case_id: str, run_dir: Path) -> None:
    if case_id not in CASES:
        raise ProbeError(f"unknown case: {case_id}")
    state = build_prefix(run_dir, case_id)
    store: RunStore = state["store"]
    if case_id == "C1":
        store.log("deterministic_crash", case_id=case_id, crash_point=CASES[case_id], last_commit=store.current_commit_id)
    else:
        provider_submit(run_dir, state["dispatch_sha"], store)
        if case_id == "C2":
            store.log("deterministic_crash", case_id=case_id, crash_point=CASES[case_id], last_commit=store.current_commit_id, runtime_remote_id_persisted=False)
        elif case_id == "C3":
            provider_set_running(run_dir, store)
            store.log("deterministic_crash", case_id=case_id, crash_point=CASES[case_id], last_commit=store.current_commit_id, provider_state="running")
        else:
            persist_running(store, state["dispatch_sha"], state["effect_ref"])
            provider_set_running(run_dir, store)
            completed = provider_complete(run_dir, store, state["packet"], "records/EFF-0002.md")
            crash = load_json(run_dir / "crash.json")
            crash["last_commit_before_crash"] = store.current_commit_id
            write_json(run_dir / "crash.json", crash)
            metrics = load_json(run_dir / "phase1_metrics.json")
            metrics["last_commit_before_crash"] = store.current_commit_id
            write_json(run_dir / "phase1_metrics.json", metrics)
            store.log("deterministic_crash", case_id=case_id, crash_point=CASES[case_id], last_commit=store.current_commit_id, return_ref=completed["return_ref"], p3_adoption=False)
    os._exit(EXIT_CRASH)


def recover_case(case_id: str, run_dir: Path) -> dict[str, Any]:
    if case_id not in CASES:
        raise ProbeError(f"unknown case: {case_id}")
    store = hydrate_store(run_dir)
    crash = load_json(run_dir / "crash.json")
    if crash.get("case_id") != case_id or crash.get("crash_point") != CASES[case_id]:
        raise ProbeError("crash metadata does not match requested case")
    packet = read_frontmatter(run_dir / "packets" / f"{DISPATCH_ID}.md")
    dispatch_sha = sha256_file(run_dir / "packets" / f"{DISPATCH_ID}.md")
    effect_intended_ref = latest_ref(store, "effect", "EFF-INT-001")
    payloads = base_payloads("workspace/input.txt", "workspace/output/output.txt")
    payloads["budget"]["measured_at"] = store.run_time
    method_ref = latest_ref(store, "validation_method", "VM-CLM-A1-A7")
    plan_ref = latest_ref(store, "execution_plan", "PLAN-W-PHASE0")
    definition_ref = latest_ref(store, "work_definition", "DEF-W-PHASE0")

    metrics = load_json(run_dir / "phase1_metrics.json")
    metrics["recovery_run_id"] = f"{case_id}-recovery-{utc_now()}"
    journal_path = provider_path(run_dir)
    if journal_path.exists():
        journal = load_json(journal_path)
        if journal["dispatch_digest"] != dispatch_sha or journal["idempotency_key"] != f"{WORK_ID}:{LOGICAL_INTENT_ID}:output-v1":
            raise ProbeError("provider journal identity failed recovery validation")
    else:
        journal = None
    reconcile_count = int(metrics.get("reconcile_count", 0)) + 1
    metrics["reconcile_count"] = reconcile_count
    store.log("provider_reconcile", case_id=case_id, reconcile_count=reconcile_count, provider_state=journal["state"] if journal else "not_submitted")

    if journal is None:
        journal = provider_submit(run_dir, dispatch_sha, store)
    persist_running(store, dispatch_sha, effect_intended_ref)
    completed = provider_complete(run_dir, store, packet, "records/EFF-0002.md")
    adopt_and_close(store, packet, dispatch_sha, method_ref, plan_ref, definition_ref, payloads, completed["observation_ref"], completed["return_ref"], completed["return_sha"])
    store.rebuild_projection_from_source()
    queried = OperationController(store).query("OP-0005")
    reconciled = OperationController(store).reconcile("OP-0005")
    store.log("operation_mechanism_check", query_state=queried["state"], adoption_status=queried["adoption_status"], reconcile_state=reconciled["state"])

    journal = load_json(journal_path)
    log_events = [json.loads(line) for line in (run_dir / "run.log").read_text(encoding="utf-8").splitlines() if line.strip()]
    return_count = len(list((run_dir / "inbox" / "untrusted").glob("RET-*.md")))
    adoption_count = len([event for event in log_events if event.get("event") == "p3_adoption"])
    invocation_count = journal["invocation_count"]
    effect_count = journal["effect_count"]
    final_projection = read_frontmatter(run_dir / "WORK_INDEX.md")
    final_state = read_frontmatter(run_dir / Path(final_projection["payload"]["work_state_ref"]))
    final_control = read_frontmatter(run_dir / Path(final_projection["payload"]["work_control_ref"]))
    commits = sorted((read_frontmatter(path)["payload"]["new_state_revision"], path) for path in (run_dir / "commits").glob("COM-*.md"))
    final_validation = verify_run(run_dir, validate_manifest(), EXPECTED)
    metrics.update({
        "provider_invocation_count": invocation_count, "provider_effect_count": effect_count, "return_count": return_count, "adoption_count": adoption_count,
        "final_checkpoint": final_state["payload"]["checkpoint"], "final_disposition": final_control["payload"]["terminal_disposition"], "last_commit_after_recovery": commits[-1][0] and f"COM-{commits[-1][0]:04d}",
        "invariants": {
            "duplicate_effect": invocation_count == 1 and effect_count == 1 and len([event for event in log_events if event.get("event") == "worker_invocation"]) == 1,
            "false_close": final_state["payload"]["checkpoint"] == "closed" and final_control["payload"]["lifecycle_state"] == "terminated" and final_control["payload"]["terminal_disposition"] == "completed",
            "no_guessing": all(read_frontmatter(path)["payload"]["state"] != "unknown" for path in (run_dir / "records").glob("OP-*.md")),
            "single_adoption": adoption_count == 1 and latest(store, "delegated_operation", "OP-INT-001")["payload"]["adoption_status"] == "adopted",
            "commit_chain": all(read_frontmatter(path)["payload"]["expected_state_revision"] == revision - 1 for revision, path in commits),
            "projection_rebuild": store.rebuild_projection_from_source()["state_revision"] == commits[-1][0],
            "authority": latest(store, "delegated_operation", "OP-INT-001")["actor"]["role"] == "P3" and latest(store, "work_state", "WS-W-PHASE0")["actor"]["role"] == "P6",
        },
        "final_runtime_validation": final_validation,
    })
    write_json(run_dir / "phase1_metrics.json", metrics)
    result = {"status": "PASS" if all(metrics["invariants"].values()) and final_validation["status"] == "PASS" and metrics["final_checkpoint"] == "closed" else "FAIL", "case_id": case_id, "run_path": relative_run(run_dir), "metrics": metrics}
    write_json(run_dir / "phase1_result.json", result)
    return result


def verify_case(case_id: str, run_dir: Path) -> dict[str, Any]:
    metrics = load_json(run_dir / "phase1_metrics.json")
    result = load_json(run_dir / "phase1_result.json")
    if metrics.get("case_id") != case_id:
        raise ProbeError("metrics case mismatch")
    if result.get("status") != "PASS":
        return result
    if not all(metrics.get("invariants", {}).values()):
        return {"status": "FAIL", "case_id": case_id, "error": "invariant failure", "metrics": metrics}
    return result


def run_matrix() -> dict[str, Any]:
    validate_manifest()
    root = RUNNER_ROOT / "runs" / "phase1"
    root.mkdir(parents=True, exist_ok=True)
    cases = []
    script = Path(__file__).resolve()
    for case_id in CASES:
        run_dir = root / case_id
        if run_dir.exists():
            raise ProbeError(f"case directory already exists; remove only this exact directory before rerun: {run_dir}")
        if OUTPUT_PATH.exists():
            OUTPUT_PATH.unlink()
        started = subprocess.run([sys.executable, str(script), "start", "--case", case_id, "--run", str(run_dir)], cwd=RUNNER_ROOT, check=False)
        if started.returncode != EXIT_CRASH:
            raise ProbeError(f"{case_id} did not terminate at deterministic crash point ({started.returncode})")
        recovered = subprocess.run([sys.executable, str(script), "recover", "--case", case_id, "--run", str(run_dir)], cwd=RUNNER_ROOT, check=False, capture_output=True, text=True)
        if recovered.returncode != 0:
            raise ProbeError(f"{case_id} recovery failed: {recovered.stdout}\n{recovered.stderr}")
        cases.append(json.loads(recovered.stdout))
    result = {"status": "PASS" if all(item["status"] == "PASS" for item in cases) else "FAIL", "manifest_root": SPEC_RUNTIME_ROOT.relative_to(RUNNER_ROOT).as_posix(), "finding_classification": FINDING_CLASSIFICATION, "cases": cases}
    write_json(root / "phase1_matrix.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic FPO Phase 1 crash-durability probe")
    parser.add_argument("command", choices=("start", "recover", "verify", "matrix", "manifest"), nargs="?", default="matrix")
    parser.add_argument("--case", choices=tuple(CASES), default=None)
    parser.add_argument("--run", dest="run_path", default=None)
    args = parser.parse_args()
    try:
        if args.command == "manifest":
            info = validate_manifest()
            result = {"status": "PASS", "manifest_path": relative_run(RUNNER_ROOT / "fpo-spec" / "Fluid_Progress_Orchestration_v0.2_Architectural_Hardening_Candidate" / "runtime" / "RUNTIME_MANIFEST.md"), "spec_runtime_root": SPEC_RUNTIME_ROOT.relative_to(RUNNER_ROOT).as_posix(), "manifest_file_count": info["manifest_file_count"], "unresolved": 0, "hash_mismatch": 0, "resolver_events": info["resolver_events"]}
        elif args.command == "matrix":
            result = run_matrix()
        else:
            if args.case is None or args.run_path is None:
                raise ProbeError(f"{args.command} requires --case and --run")
            run_dir = Path(args.run_path).resolve()
            if args.command == "start":
                crash_start(args.case, run_dir)
                return EXIT_CRASH
            if args.command == "recover":
                result = recover_case(args.case, run_dir)
            else:
                result = verify_case(args.case, run_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    except (ProbeError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
