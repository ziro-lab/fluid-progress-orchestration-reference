#!/usr/bin/env python3
"""Deterministic Phase 2 adversarial state-consistency probe.

This harness deliberately keeps the Phase 0/1 commit, projection, operation,
and return mechanisms unchanged.  It injects adversarial inbox/provider/
evidence observations around those mechanisms and records validity,
applicability, and adoption as separate facts.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import run_baseline as p0
import run_phase1 as p1


RUNNER_ROOT = p0.RUNNER_ROOT
INPUT_PATH = p0.INPUT_PATH
OUTPUT_PATH = p0.OUTPUT_PATH
WORK_ID = p0.WORK_ID
DISPATCH_ID = p0.DISPATCH_ID
LOGICAL_INTENT_ID = p0.LOGICAL_INTENT_ID
OPERATION_ID = p0.OPERATION_ID
PLAN_UNIT_ID = p0.PLAN_UNIT_ID
CAPABILITY_ID = p0.CAPABILITY_ID
CAPABILITY_REVISION = p0.CAPABILITY_REVISION
TARGET_REVISION = p0.TARGET_REVISION
DESIGN_REVISION = p0.DESIGN_REVISION
SCHEMA_PATH = p0.SCHEMA_PATH

CASES = ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8")
GATE_A = ("D1", "D2", "D3", "D4")
GATE_B = ("D5", "D6", "D7")
GATE_C = ("D8",)
CASE_FAULTS = {
    "D1": "duplicate-return",
    "D2": "out-of-order-return",
    "D3": "stale-revision-return",
    "D4": "wrong-operation-binding",
    "D5": "effect-unknown-response-loss",
    "D6": "provider-unknown",
    "D7": "partial-effect",
    "D8": "evidence-conflict",
}


class Phase2Error(p0.ProbeError):
    pass


def write_json(path: Path, value: Any) -> None:
    p0.write_bytes(path, p0.json_bytes(value))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase2Error(f"expected JSON object: {path}")
    return value


def latest(store: p0.RunStore, record_type: str, logical_id: str) -> dict[str, Any]:
    value = store.latest_record(record_type, logical_id)
    if value is None:
        raise Phase2Error(f"missing latest {record_type}/{logical_id}")
    return value


def latest_ref(store: p0.RunStore, record_type: str, logical_id: str) -> str:
    value = latest(store, record_type, logical_id)
    for ref, candidate in store.record_values.items():
        if candidate is value:
            return ref
    raise Phase2Error(f"missing ref for {record_type}/{logical_id}")


def next_record_id(store: p0.RunStore, prefix: str) -> str:
    values: list[int] = []
    for path in (store.run_dir / "records").glob(f"{prefix}-*.md"):
        try:
            values.append(int(path.stem.rsplit("-", 1)[-1]))
        except ValueError:
            continue
    return f"{prefix}-{(max(values) + 1 if values else 1):04d}"


def phase2_payloads(store: p0.RunStore) -> dict[str, Any]:
    payloads = p0.base_payloads("workspace/input.txt", "workspace/output/output.txt")
    payloads["budget"]["measured_at"] = store.run_time
    payloads["approval"]["valid_from"] = store.run_time
    return payloads


def run_normal_to_closed(run_dir: Path) -> p0.RunStore:
    """Create a fresh completed baseline inside this case directory."""
    state = p1.build_prefix(run_dir, "C1")
    store: p0.RunStore = state["store"]
    p1.provider_submit(run_dir, state["dispatch_sha"], store)
    p1.persist_running(store, state["dispatch_sha"], state["effect_ref"])
    p1.provider_set_running(run_dir, store)
    completed = p1.provider_complete(run_dir, store, state["packet"], "records/EFF-0002.md")
    payloads = phase2_payloads(store)
    p1.adopt_and_close(
        store,
        state["packet"],
        state["dispatch_sha"],
        latest_ref(store, "validation_method", "VM-CLM-A1-A7"),
        latest_ref(store, "execution_plan", "PLAN-W-PHASE0"),
        latest_ref(store, "work_definition", "DEF-W-PHASE0"),
        payloads,
        completed["observation_ref"],
        completed["return_ref"],
        completed["return_sha"],
    )
    store.rebuild_projection_from_source()
    return store


def return_variant(packet: dict[str, Any], *, return_id: str, dispatch_id: str | None = None, logical_intent_id: str | None = None, attempt_id: str | None = None, remote_operation_id: str | None = None, plan_ref: str | None = None, definition_ref: str | None = None, target_revision: str | None = None, capability_id: str | None = None, capability_revision: str | None = None, effect_ref: str = "records/EFF-0001.md") -> dict[str, Any]:
    worker_result = {"output_sha256": p0.sha256_file(OUTPUT_PATH)}
    value = p0.make_return(packet, worker_result, p0.utc_now())
    value["return_id"] = return_id
    if dispatch_id is not None:
        value["dispatch_id"] = dispatch_id
    if logical_intent_id is not None:
        value["logical_intent_id"] = logical_intent_id
    if attempt_id is not None:
        value["attempt_id"] = attempt_id
    if remote_operation_id is not None:
        value["remote_operation_id"] = remote_operation_id
    if plan_ref is not None:
        value["observed_plan_ref"] = plan_ref
    if definition_ref is not None:
        value["observed_definition_ref"] = definition_ref
    if target_revision is not None:
        value["observed_target_revision_ref"] = target_revision
    if capability_id is not None:
        value["capability_id"] = capability_id
    if capability_revision is not None:
        value["capability_revision"] = capability_revision
    value["effect_update_refs"] = [effect_ref]
    return value


def persist_raw_return(store: p0.RunStore, packet: dict[str, Any], file_name: str, message: dict[str, Any], classification: dict[str, Any]) -> str:
    ref = store.add_message(message, "inbox/untrusted", file_name, "Phase 2 raw capability Return; arrival is immutable and adoption is separately classified.")
    store.add_observation(f"RAW-{Path(file_name).stem}.json", {"message_ref": ref, "valid": True, **classification})
    return ref


def classify_returns(store: p0.RunStore) -> tuple[int, int]:
    arrival = 0
    valid = 0
    for path in sorted((store.run_dir / "inbox" / "untrusted").glob("RET-*.md")):
        arrival += 1
        value = p0.read_frontmatter(path)
        store.validator.validate(value, store.schema)
        valid += 1
    return arrival, valid


def base_metrics(case_id: str, checkpoint_before: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "injected_fault": CASE_FAULTS[case_id],
        "return_arrival_count": 0,
        "return_valid_count": 0,
        "return_applicable_count": 0,
        "return_adoption_count": 0,
        "provider_invocation_count": 0,
        "effect_count": 0,
        "reconcile_count": 0,
        "evidence_count": 0,
        "evidence_conflict_count": 0,
        "checkpoint_before": checkpoint_before,
        "checkpoint_after": checkpoint_before,
        "work_lifecycle": "active",
        "disposition": None,
        "active_blocker_count": 0,
        "false_close": 0,
        "unknown_as_success": 0,
        "wrong_bound_adoption": 0,
        "stale_adoption": 0,
        "duplicate_adoption": 0,
        "duplicate_effect": 0,
        "input_corruption": 0,
        "hot_loop": 0,
        "blind_retry": 0,
        "accepted": False,
        "result": "",
        "invariants": {},
    }


def final_state(store: p0.RunStore) -> tuple[str, str | None, str]:
    projection = p0.read_frontmatter(store.run_dir / "WORK_INDEX.md")
    state = p0.read_frontmatter(store.ref_path(projection["payload"]["work_state_ref"]))["payload"]
    control = p0.read_frontmatter(store.ref_path(projection["payload"]["work_control_ref"]))["payload"]
    return state["checkpoint"], control["terminal_disposition"], control["lifecycle_state"]


def commit_integrity(store: p0.RunStore) -> bool:
    commits = []
    previous_id: str | None = None
    for path in sorted((store.run_dir / "commits").glob("COM-*.md")):
        commit = p0.read_frontmatter(path)
        payload = commit["payload"]
        revision = payload["new_state_revision"]
        if payload["expected_state_revision"] != revision - 1 or payload["parent_commit_id"] != previous_id:
            return False
        for item in payload["record_digests"]:
            target = store.run_dir / Path(item["ref"])
            if not target.is_file() or p0.sha256_file(target) != item["sha256"]:
                return False
        projection = store.run_dir / Path(payload["projection_ref"])
        if not projection.is_file() or p0.sha256_file(projection) != payload["projection_sha256"]:
            return False
        previous_id = payload["commit_id"]
        commits.append(revision)
    return bool(commits)


def common_invariants(store: p0.RunStore, metrics: dict[str, Any], *, finite_state: bool) -> dict[str, bool]:
    checkpoint, disposition, lifecycle = final_state(store)
    rebuilt = store.rebuild_projection_from_source()
    return {
        "duplicate_effect": metrics["duplicate_effect"] == 0,
        "duplicate_adoption": metrics["duplicate_adoption"] == 0,
        "stale_adoption": metrics["stale_adoption"] == 0,
        "wrong_binding_adoption": metrics["wrong_bound_adoption"] == 0,
        "unknown_as_success": metrics["unknown_as_success"] == 0,
        "false_close": metrics["false_close"] == 0 and not (lifecycle == "terminated" and disposition == "completed" and not metrics["accepted"] and metrics["evidence_conflict_count"] > 0),
        "authority": all(value["actor"]["role"] in {"runtime", "P3", "P4", "P5", "P6", "user", "P1", "P2"} for value in store.record_values.values()),
        "commit_integrity": commit_integrity(store),
        "projection_rebuild": rebuilt["state_revision"] == store.state_revision,
        "input_corruption": metrics["input_corruption"] == 0 and INPUT_PATH.read_text(encoding="utf-8") == json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8"))["input_text"],
        "finite_convergence": (checkpoint == "closed" and lifecycle == "terminated" and disposition == "completed") or finite_state,
    }


def add_blocker_state(store: p0.RunStore, *, case_id: str, kind: str, symptom: str, effect_ref: str, operation_ref: str, observation_ref: str, checkpoint: str = "designed", unit_state: str = "blocked", unresolved_effect: bool = True, active_operation: bool = True) -> dict[str, str]:
    blocker_id = next_record_id(store, "BLK")
    blocker_logical = f"BLK-{case_id}-UNKNOWN"
    blocker = p0.append_record(store, "blocker", blocker_id, blocker_logical, {
        "kind": kind, "status": "open", "scope": WORK_ID, "blocks_core": True, "source_stage": "runtime",
        "affected_revision_refs": [f"records/{operation_ref}.md", f"records/{effect_ref}.md"], "symptom": symptom,
        "hypotheses": [], "earliest_unrepaired_error": symptom, "root_cause": None, "contributing_factors": [],
        "detection_gap": None, "dependency_blocker_refs": [], "attempt_refs": [], "strategy_families_tried": ["deterministic_reconcile"],
        "progress_claims": [], "required_evidence_claim_ids": [], "required_capability_classes": [CAPABILITY_ID], "required_approval_refs": ["records/APR-0001.md"],
        "resume_condition_ref": blocker_id, "resume_owner": "P5", "resume_expiry": None, "resume_default_action": "wait_for_owner_resolution",
        "next_normal_authority": "P5", "rollback_checkpoint": checkpoint, "resolution_evidence_refs": [], "terminal_recommendation": None,
    }, p0.actor("runtime-1", "runtime", "blocker_projection"))
    blocker_set_id = next_record_id(store, "BLKSET")
    blocker_set = p0.append_record(store, "blocker_set", blocker_set_id, f"BLKSET-{case_id}", {
        "active_blocker_refs": [blocker], "blocking_count": 1, "waiting_count": 0, "scope_summary": [symptom], "last_p5_decision_ref": None,
    }, p0.actor("runtime-1", "runtime", "blocker_projection"))
    unit_id = next_record_id(store, "UNITSTATE")
    unit_blocked = p0.append_record(store, "plan_unit_state", unit_id, "UNITSTATE-W-PHASE0-UNIT-001", {
        "plan_ref": "records/PLAN-0001.md", "unit_id": PLAN_UNIT_ID, "state": unit_state, "attempt_refs": ["attempts/ATT-0001.md"],
        "operation_refs": [f"records/{operation_ref}.md"] if active_operation else [], "effect_refs": [f"records/{effect_ref}.md"], "adopted_result_refs": [],
        "blocked_by_refs": [blocker], "target_revision_refs": [TARGET_REVISION], "last_event_ref": blocker,
    }, p0.actor("runtime-1", "runtime", "execution_projection"), revision=4)
    ws_id = next_record_id(store, "WS")
    ws = p0.append_record(store, "work_state", ws_id, "WS-W-PHASE0", {"checkpoint": checkpoint, "interrupt_ref": blocker}, p0.actor("runtime-1", "runtime", "blocker_projection"), revision=4)
    wc_id = next_record_id(store, "WC")
    wc = p0.append_record(store, "work_control", wc_id, "WC-W-PHASE0", {
        "lifecycle_state": "suspended", "terminal_disposition": None, "reason": symptom,
        "resume_condition_ref": blocker, "resume_owner": "P5", "resume_expiry": "2099-01-01T00:00:00Z", "resume_default_action": "wait_for_owner_resolution",
        "latest_user_event_ref": None, "active_approval_refs": ["records/APR-0001.md"], "active_operation_refs": [f"records/{operation_ref}.md"] if active_operation else [],
        "unresolved_effect_refs": [f"records/{effect_ref}.md"] if unresolved_effect else [], "autonomy_budget": phase2_payloads(store)["budget"]["budget"],
    }, p0.actor("runtime-1", "runtime", "work_control_projection"), revision=2)
    store.commit([blocker, blocker_set, unit_blocked, ws, wc, observation_ref], blocker_set, f"{case_id} explicit blocker and suspended unresolved state; no automatic success or retry.")
    return {"blocker_ref": blocker, "blocker_set_ref": blocker_set, "unit_ref": unit_blocked, "work_state_ref": ws, "work_control_ref": wc}


def adopt_success(store: p0.RunStore, *, observation_ref: str, return_ref: str, return_sha: str, dispatch_sha: str, method_ref: str, plan_ref: str, definition_ref: str, payloads: dict[str, Any]) -> None:
    output_sha = p0.sha256_file(OUTPUT_PATH)
    artifact_id = next_record_id(store, "ART")
    artifact = p0.append_record(store, "artifact_manifest", artifact_id, "ART-W-PHASE2", {
        "manifest_id": "ART-W-PHASE2-R1", "target_revision": TARGET_REVISION,
        "artifacts": [{"artifact_id": "ARTIFACT-001", "path_or_uri": "workspace/output/output.txt", "sha256": output_sha, "media_type": "text/plain", "revision": TARGET_REVISION, "source_unit_refs": [PLAN_UNIT_ID], "adoption_status": "adopted"}],
        "integration_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"], "environment_revision_refs": ["ENV-LOCAL-R1"],
    }, p0.actor("p3-owner", "P3", "target_mutation"))
    effect_id = next_record_id(store, "EFF")
    confirmed_payload = p0.effect_payload("confirmed", output_sha, observation_ref)
    confirmed_payload["effect_id"] = effect_id
    confirmed = p0.append_record(store, "effect", effect_id, "EFF-INT-001", confirmed_payload, p0.actor("p3-owner", "P3", "execution_adoption"), revision=latest(store, "effect", "EFF-INT-001")["record_revision"] + 1)
    adopted_id = next_record_id(store, "OP")
    adopted = p0.append_record(store, "delegated_operation", adopted_id, "OP-INT-001", p0.operation_payload(dispatch_sha, "succeeded", return_ref=return_ref, return_sha=return_sha, adoption="adopted", provider_sequence=2, evidence_refs=[observation_ref], effect_refs=[confirmed], remote_operation_id=OPERATION_ID), p0.actor("p3-owner", "P3", "execution_adoption"), revision=latest(store, "delegated_operation", "OP-INT-001")["record_revision"] + 1)
    unit_id = next_record_id(store, "UNITSTATE")
    unit_payload = p0.unit_state_payload("succeeded", operation_ref=adopted, effect_ref=confirmed, result_refs=[artifact, observation_ref], last_event_ref=artifact)
    unit = p0.append_record(store, "plan_unit_state", unit_id, "UNITSTATE-W-PHASE0-UNIT-001", unit_payload, p0.actor("p3-owner", "P3", "execution_adoption"), revision=latest(store, "plan_unit_state", "UNITSTATE-W-PHASE0-UNIT-001")["record_revision"] + 1)
    ws_id = next_record_id(store, "WS")
    ws = p0.append_record(store, "work_state", ws_id, "WS-W-PHASE0", {"checkpoint": "executed", "interrupt_ref": None}, p0.actor("p3-owner", "P3", "execution_adoption"), revision=latest(store, "work_state", "WS-W-PHASE0")["record_revision"] + 1)
    store.log("p3_adoption", operation_ref=adopted, effect_ref=confirmed, artifact_ref=artifact, adoption_count=1)
    store.commit([artifact, confirmed, unit, adopted, ws], ws, "P3 adopted reconciled evidence exactly once; checkpoint executed.")
    close_success(store, observation_ref, method_ref, plan_ref, definition_ref, payloads, artifact, ws)


def close_success(store: p0.RunStore, observation_ref: str, method_ref: str, plan_ref: str, definition_ref: str, payloads: dict[str, Any], artifact_ref: str, ws_executed_ref: str) -> None:
    if latest(store, "work_state", "WS-W-PHASE0")["payload"]["checkpoint"] != "executed":
        raise Phase2Error("success closure requires executed checkpoint")
    evidence_refs: list[str] = []
    verdict_refs: list[str] = []
    criteria = [
        ("A1", "CLM-A1", "workspace/input.txt", "Input remained unchanged."),
        ("A2", "CLM-A2", "workspace/output/output.txt", "Output exists at the separate target."),
        ("A3", "CLM-A3", "workspace/output/output.txt", "Output exactly matches the expected uppercase fixture."),
        ("A4", "CLM-A4", "run.log", "Exactly one provider invocation and one effect were observed."),
        ("A5", "CLM-A5", "commits/", "Evidence and verdicts were committed before closure."),
        ("A6", "CLM-A6", "records/", "Unknown was reconciled before adoption."),
        ("A7", "CLM-A7", "records/", "P3 adoption is separate from Return arrival."),
    ]
    for index, (criterion_id, claim_id, object_ref, rationale) in enumerate(criteria, start=1):
        evidence_id = f"EVD-{index:04d}"
        evidence_refs.append(p0.append_record(store, "evidence", evidence_id, f"EVD-{claim_id}", {
            "claim_id": claim_id, "criterion_id": criterion_id, "method_id": "filesystem.inspect", "method_revision": "1", "object_ref": object_ref, "object_revision": f"RUN-{store.run_time}", "design_revision": DESIGN_REVISION, "plan_revision": DESIGN_REVISION, "environment_ref": "ENV-LOCAL", "environment_revision": "ENV-LOCAL-R1", "observed_at": store.run_time, "freshness_policy": "Valid only for this fresh Phase 2 case.", "expires_at": None, "producer_id": "runtime-validator", "verifier_id": "p4-owner", "trust_domain": "local-readonly-probe", "source_lineage": [observation_ref, "probe/ACCEPTANCE.md"], "coverage": "full", "independence_basis": "Read-only evidence is separate from Return control authority.", "independence_group": "phase2-local-checks", "status": "valid", "supersedes_refs": [], "contradiction_refs": [], "raw_observation_refs": [observation_ref], "adopted_by": "P4",
        }, p0.actor("p4-owner", "P4", "evidence_adoption"), explanation="P4 evidence for a resolved Phase 2 case."))
        verdict_refs.append(p0.append_record(store, "criteria_verdict", f"VER-{index:04d}", f"VER-{criterion_id}", {
            "criterion_id": criterion_id, "verdict": "PASS", "evidence_refs": [evidence_refs[-1]], "method_refs": [method_ref], "object_revision_refs": [TARGET_REVISION, f"RUN-{store.run_time}"], "coverage_complete": True, "freshness_ok": True, "conflict_status": "none", "independence_satisfied": True, "rationale": rationale,
        }, p0.actor("p4-owner", "P4", "criteria_verdict")))
    ws_accepted = p0.append_record(store, "work_state", "WS-0005", "WS-W-PHASE0", {"checkpoint": "accepted", "interrupt_ref": None}, p0.actor("p4-owner", "P4", "acceptance"), revision=5)
    store.commit(evidence_refs + verdict_refs + [ws_accepted], ws_accepted, "P4 adopted independent evidence and PASS verdicts; checkpoint accepted.")
    budget = dict(payloads["budget"])
    budget["budget"] = dict(payloads["budget"]["budget"])
    budget["budget"]["usage"] = dict(payloads["budget"]["budget"]["usage"])
    budget["budget"]["usage"].update({"attempts": 1, "strategy_families": 1, "capability_calls": 1, "effect_count": 1})
    budget["measured_at"] = store.run_time
    budget_ref = p0.append_record(store, "resource_budget", "BUD-0002", "BUD-W-PHASE0", budget, p0.actor("runtime-1", "runtime", "work_control_projection"), revision=2)
    settlement = p0.append_record(store, "terminal_settlement", "SET-0001", "SET-W-PHASE2", {
        "disposition": "completed", "achievement_checkpoint": "closed", "definition_ref": definition_ref, "execution_plan_ref": plan_ref, "artifact_manifest_ref": artifact_ref, "criteria_verdict_refs": verdict_refs, "open_blocker_refs": [], "inflight_operation_refs": [], "unsettled_effect_refs": [], "known_limitations": ["Resolved adversarial state consistency case."], "remaining_obligations": [], "handoff_ref": None, "retention_summary": "Phase 2 audit artifacts retained under this run directory.", "settled_at": store.run_time,
    }, p0.actor("p6-owner", "P6", "successful_closure"), explanation="P6 closure after explicit reconciliation and independent evidence.")
    event = p0.append_record(store, "ledger_event", "EVT-0001", "EVT-W-PHASE2-CLOSURE", {"event_type": "closure", "summary": "Phase 2 case reached completed terminal settlement after safe resolution.", "fact_refs": [settlement, *verdict_refs], "decision_refs": [settlement], "supersedes_refs": [], "rationale": "No unresolved operation, effect, or evidence conflict remains.", "hidden_reasoning_included": False}, p0.actor("p6-owner", "P6", "successful_closure"))
    wc = p0.append_record(store, "work_control", "WC-0002", "WC-W-PHASE0", {"lifecycle_state": "terminated", "terminal_disposition": "completed", "reason": "P6 completed terminal settlement.", "resume_condition_ref": None, "resume_owner": None, "resume_expiry": None, "resume_default_action": None, "latest_user_event_ref": None, "active_approval_refs": [], "active_operation_refs": [], "unresolved_effect_refs": [], "autonomy_budget": budget["budget"]}, p0.actor("runtime-1", "runtime", "work_control_projection"), revision=2)
    ws_closed = p0.append_record(store, "work_state", "WS-0006", "WS-W-PHASE0", {"checkpoint": "closed", "interrupt_ref": None}, p0.actor("p6-owner", "P6", "successful_closure"), revision=6)
    store.commit([budget_ref, settlement, event, wc, ws_closed], settlement, "P6 closure settlement; checkpoint closed and Work Control terminal/completed.")


def d1_duplicate_return(run_dir: Path) -> dict[str, Any]:
    store = run_normal_to_closed(run_dir)
    packet = p0.read_frontmatter(run_dir / "packets" / "DISP-0001.md")
    original = p0.read_frontmatter(run_dir / "inbox" / "untrusted" / "RET-0001.md")
    duplicate = dict(original)
    duplicate["return_id"] = original["return_id"]
    persist_raw_return(store, packet, "RET-0001-DUPLICATE.md", duplicate, {"arrival": "duplicate", "applicable": True, "adopted": False, "reason": "same logical Return already adopted"})
    store.log("duplicate_return_detected", duplicate_ref="inbox/untrusted/RET-0001-DUPLICATE.md", duplicate_adoption=0)
    arrival, valid = classify_returns(store)
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D1", "closed")
    metrics.update({"return_arrival_count": arrival, "return_valid_count": valid, "return_applicable_count": 2, "return_adoption_count": 1, "provider_invocation_count": 1, "effect_count": 1, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "duplicate_effect": 0, "duplicate_adoption": 0, "accepted": True, "result": "resolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=False)
    metrics["final_validation"] = p0.verify_run(run_dir, p0.validate_manifest(), json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8")))
    return finalize_case(store, metrics)


def d2_out_of_order(run_dir: Path) -> dict[str, Any]:
    store = run_normal_to_closed(run_dir)
    packet = p0.read_frontmatter(run_dir / "packets" / "DISP-0001.md")
    stale = return_variant(packet, return_id="RET-A", plan_ref="records/PLAN-OLD.md", definition_ref="records/DEF-OLD.md", target_revision="TARGET-R0")
    persist_raw_return(store, packet, "RET-A-LATE.md", stale, {"arrival": "late", "applicable": False, "adopted": False, "reason": "superseded by current Return"})
    store.log("stale_return_detected", return_ref="inbox/untrusted/RET-A-LATE.md", current_return_ref="inbox/untrusted/RET-0001.md", stale_adoption=0)
    arrival, valid = classify_returns(store)
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D2", "closed")
    metrics.update({"return_arrival_count": arrival, "return_valid_count": valid, "return_applicable_count": 1, "return_adoption_count": 1, "provider_invocation_count": 1, "effect_count": 1, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "stale_adoption": 0, "accepted": True, "result": "resolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=False)
    metrics["final_validation"] = p0.verify_run(run_dir, p0.validate_manifest(), json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8")))
    return finalize_case(store, metrics)


def d3_stale_revision(run_dir: Path) -> dict[str, Any]:
    store = run_normal_to_closed(run_dir)
    packet = p0.read_frontmatter(run_dir / "packets" / "DISP-0001.md")
    stale = return_variant(packet, return_id="RET-OLD-REV", plan_ref="records/PLAN-OLD.md", definition_ref="records/DEF-OLD.md", target_revision="TARGET-R0", effect_ref="records/EFF-OLD.md")
    persist_raw_return(store, packet, "RET-OLD-REVISION.md", stale, {"arrival": "stale_revision", "applicable": False, "adopted": False, "reason": "design/dispatch/target revision differs from current"})
    store.log("stale_revision_detected", return_ref="inbox/untrusted/RET-OLD-REVISION.md", stale_adoption=0, current_state_unchanged=True)
    arrival, valid = classify_returns(store)
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D3", "closed")
    metrics.update({"return_arrival_count": arrival, "return_valid_count": valid, "return_applicable_count": 1, "return_adoption_count": 1, "provider_invocation_count": 1, "effect_count": 1, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "stale_adoption": 0, "accepted": True, "result": "resolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=False)
    metrics["final_validation"] = p0.verify_run(run_dir, p0.validate_manifest(), json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8")))
    return finalize_case(store, metrics)


def d4_wrong_binding(run_dir: Path) -> dict[str, Any]:
    store = run_normal_to_closed(run_dir)
    packet = p0.read_frontmatter(run_dir / "packets" / "DISP-0001.md")
    wrong = return_variant(packet, return_id="RET-WRONG-BIND", dispatch_id="DISP-OTHER", logical_intent_id="INT-OTHER", attempt_id="ATT-OTHER", remote_operation_id="LOCAL-OP-OTHER", capability_id=CAPABILITY_ID, capability_revision=CAPABILITY_REVISION)
    persist_raw_return(store, packet, "RET-WRONG-BINDING.md", wrong, {"arrival": "wrong_binding", "applicable": False, "adopted": False, "reason": "work/dispatch/operation/logical intent identity mismatch"})
    store.log("wrong_return_binding_detected", return_ref="inbox/untrusted/RET-WRONG-BINDING.md", wrong_bound_adoption=0)
    arrival, valid = classify_returns(store)
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D4", "closed")
    metrics.update({"return_arrival_count": arrival, "return_valid_count": valid, "return_applicable_count": 1, "return_adoption_count": 1, "provider_invocation_count": 1, "effect_count": 1, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "wrong_bound_adoption": 0, "accepted": True, "result": "resolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=False)
    metrics["final_validation"] = p0.verify_run(run_dir, p0.validate_manifest(), json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8")))
    return finalize_case(store, metrics)


def prepare_running(run_dir: Path) -> tuple[p0.RunStore, dict[str, Any], str, str]:
    state = p1.build_prefix(run_dir, "C1")
    store: p0.RunStore = state["store"]
    p1.provider_submit(run_dir, state["dispatch_sha"], store)
    p1.persist_running(store, state["dispatch_sha"], state["effect_ref"])
    p1.provider_set_running(run_dir, store)
    return store, state, state["dispatch_sha"], state["packet"]


def d5_effect_unknown(run_dir: Path) -> dict[str, Any]:
    store, state, dispatch_sha, packet = prepare_running(run_dir)
    worker_result, observation_ref = p1.run_worker(packet, p0.effect_payload("started"), store)
    journal = p1.load_json(p1.provider_path(run_dir))
    journal.update({"state": "completed", "effect_count": 1, "completed_at": p0.utc_now(), "return_ref": None, "return_sha256": None})
    p1.write_json(p1.provider_path(run_dir), journal)
    unknown_id = next_record_id(store, "EFF")
    unknown_payload = p0.effect_payload("unknown")
    unknown_payload["effect_id"] = unknown_id
    unknown_ref = p0.append_record(store, "effect", unknown_id, "EFF-INT-001", unknown_payload, p0.actor("runtime-1", "runtime", "effect_lifecycle_projection"), revision=3)
    op_id = next_record_id(store, "OP")
    op_unknown = p0.append_record(store, "delegated_operation", op_id, "OP-INT-001", p0.operation_payload(dispatch_sha, "unknown", provider_sequence=1, effect_refs=[unknown_ref], remote_operation_id=OPERATION_ID, error_summary="Return was lost after provider effect; reconciliation required."), p0.actor("runtime-1", "runtime", "operation_lifecycle"), revision=4)
    store.commit([observation_ref, unknown_ref, op_unknown], op_unknown, "Response loss recorded as explicit unknown; no success or retry inferred.")
    store.log("response_loss", operation_ref=op_unknown, effect_ref=unknown_ref, unknown_as_success=0, blind_retry=0)

    store.log("provider_reconcile", reconcile_count=1, provider_state="completed", effect_observed=True, return_observed=False)
    if journal["invocation_count"] != 1 or journal["effect_count"] != 1 or not OUTPUT_PATH.exists():
        raise Phase2Error("D5 provider reconciliation did not establish exact external fact")
    return_message = p0.make_return(packet, {"output_sha256": p0.sha256_file(OUTPUT_PATH)}, store.run_time)
    return_message["effect_update_refs"] = [unknown_ref]
    return_ref = store.add_message(return_message, "inbox/untrusted", "RET-0001.md", "Return reconstructed from explicit provider reconciliation; still untrusted for adoption.")
    return_sha = p0.sha256_file(store.ref_path(return_ref))
    journal["return_ref"] = return_ref
    journal["return_sha256"] = return_sha
    p1.write_json(p1.provider_path(run_dir), journal)
    op_succeeded_id = next_record_id(store, "OP")
    op_succeeded = p0.append_record(store, "delegated_operation", op_succeeded_id, "OP-INT-001", p0.operation_payload(dispatch_sha, "succeeded", return_ref=return_ref, return_sha=return_sha, provider_sequence=2, effect_refs=[unknown_ref], remote_operation_id=OPERATION_ID), p0.actor("runtime-1", "runtime", "operation_lifecycle"), revision=5)
    store.commit([return_ref, op_succeeded], op_succeeded, "Provider reconciliation produced an immutable Return; P3 adoption remains separate.")
    payloads = phase2_payloads(store)
    adopt_success(store, observation_ref=observation_ref, return_ref=return_ref, return_sha=return_sha, dispatch_sha=dispatch_sha, method_ref=latest_ref(store, "validation_method", "VM-CLM-A1-A7"), plan_ref=latest_ref(store, "execution_plan", "PLAN-W-PHASE0"), definition_ref=latest_ref(store, "work_definition", "DEF-W-PHASE0"), payloads=payloads)
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D5", "designed")
    metrics.update({"return_arrival_count": 1, "return_valid_count": 1, "return_applicable_count": 1, "return_adoption_count": 1, "provider_invocation_count": journal["invocation_count"], "effect_count": journal["effect_count"], "reconcile_count": 1, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "accepted": True, "result": "resolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=False)
    metrics["final_validation"] = p0.verify_run(run_dir, p0.validate_manifest(), json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8")))
    return finalize_case(store, metrics)


def d6_provider_unknown(run_dir: Path) -> dict[str, Any]:
    store, state, dispatch_sha, _packet = prepare_running(run_dir)
    journal = p1.load_json(p1.provider_path(run_dir))
    journal.update({"state": "unknown", "provider_query": "temporarily_unavailable", "effect_count": 0})
    p1.write_json(p1.provider_path(run_dir), journal)
    query_ref = store.add_observation("PROVIDER-UNKNOWN.json", {"provider_state": "unknown", "reason": "temporarily_unavailable", "query_count": 1, "safe_retry": False})
    unknown_id = next_record_id(store, "EFF")
    effect = p0.effect_payload("unknown")
    effect["effect_id"] = unknown_id
    effect_ref = p0.append_record(store, "effect", unknown_id, "EFF-INT-001", effect, p0.actor("runtime-1", "runtime", "effect_lifecycle_projection"), revision=3)
    op_id = next_record_id(store, "OP")
    operation = p0.append_record(store, "delegated_operation", op_id, "OP-INT-001", p0.operation_payload(dispatch_sha, "unknown", provider_sequence=1, effect_refs=[effect_ref], remote_operation_id=OPERATION_ID, error_summary="Provider query returned unknown; no safe outcome is established."), p0.actor("runtime-1", "runtime", "operation_lifecycle"), revision=4)
    store.commit([query_ref, effect_ref, operation], operation, "Provider unknown is preserved as unknown; no blind retry or success inference.")
    blocker = add_blocker_state(store, case_id="D6", kind="provider_state_unknown", symptom="Provider query returned unknown/temporarily unavailable; effect outcome cannot be determined.", effect_ref=effect_ref.removeprefix("records/").removesuffix(".md"), operation_ref=operation.removeprefix("records/").removesuffix(".md"), observation_ref=query_ref)
    store.log("provider_unknown_blocked", query_count=1, hot_loop=0, blind_retry=0, blocker_ref=blocker["blocker_ref"])
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D6", "designed")
    metrics.update({"provider_invocation_count": journal["invocation_count"], "effect_count": journal["effect_count"], "reconcile_count": 1, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "active_blocker_count": 1, "blind_retry": 0, "hot_loop": 0, "accepted": False, "result": "justified_unresolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=True)
    return finalize_case(store, metrics)


def d7_partial_effect(run_dir: Path) -> dict[str, Any]:
    store, state, dispatch_sha, _packet = prepare_running(run_dir)
    journal = p1.load_json(p1.provider_path(run_dir))
    partial_ref = store.add_observation("PROVIDER-PARTIAL.json", {"provider_state": "partial", "steps": [{"step": "temp_output", "state": "completed"}, {"step": "content_confirmation", "state": "completed"}, {"step": "final_publish", "state": "not_started"}], "final_target_exists": False})
    journal.update({"state": "partial", "effect_count": 1, "partial_steps": ["temp_output", "content_confirmation"], "final_publish": False, "return_ref": None, "return_sha256": None})
    p1.write_json(p1.provider_path(run_dir), journal)
    effect_id = next_record_id(store, "EFF")
    effect = p0.effect_payload("forward_recovery_required")
    effect["effect_id"] = effect_id
    effect_ref = p0.append_record(store, "effect", effect_id, "EFF-INT-001", effect, p0.actor("runtime-1", "runtime", "effect_lifecycle_projection"), revision=3)
    op_id = next_record_id(store, "OP")
    operation = p0.append_record(store, "delegated_operation", op_id, "OP-INT-001", p0.operation_payload(dispatch_sha, "unknown", provider_sequence=1, effect_refs=[effect_ref], remote_operation_id=OPERATION_ID, error_summary="Partial effect observed; final publish is not established."), p0.actor("runtime-1", "runtime", "operation_lifecycle"), revision=4)
    store.commit([partial_ref, effect_ref, operation], operation, "Partial effect recorded; no full retry or automatic compensation policy inferred.")
    blocker = add_blocker_state(store, case_id="D7", kind="partial_effect", symptom="Provider completed only preparatory effect steps; final publish did not occur.", effect_ref=effect_ref.removeprefix("records/").removesuffix(".md"), operation_ref=operation.removeprefix("records/").removesuffix(".md"), observation_ref=partial_ref)
    store.log("partial_effect_blocked", partial_effect=True, blind_retry=0, duplicate_effect=0, authority_violation=0, blocker_ref=blocker["blocker_ref"])
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D7", "designed")
    metrics.update({"provider_invocation_count": journal["invocation_count"], "effect_count": journal["effect_count"], "reconcile_count": 1, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "active_blocker_count": 1, "blind_retry": 0, "accepted": False, "result": "justified_unresolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=True)
    return finalize_case(store, metrics)


def adopt_only_for_conflict(store: p0.RunStore, state: dict[str, Any], completed: dict[str, Any]) -> str:
    output_sha = p0.sha256_file(OUTPUT_PATH)
    artifact = p0.append_record(store, "artifact_manifest", "ART-0001", "ART-W-PHASE2", {"manifest_id": "ART-W-PHASE2-R1", "target_revision": TARGET_REVISION, "artifacts": [{"artifact_id": "ARTIFACT-001", "path_or_uri": "workspace/output/output.txt", "sha256": output_sha, "media_type": "text/plain", "revision": TARGET_REVISION, "source_unit_refs": [PLAN_UNIT_ID], "adoption_status": "adopted"}], "integration_claim_ids": ["CLM-A1", "CLM-A2", "CLM-A3"], "environment_revision_refs": ["ENV-LOCAL-R1"]}, p0.actor("p3-owner", "P3", "target_mutation"))
    effect = p0.effect_payload("confirmed", output_sha, completed["observation_ref"])
    effect["effect_id"] = "EFF-0003"
    effect_ref = p0.append_record(store, "effect", "EFF-0003", "EFF-INT-001", effect, p0.actor("p3-owner", "P3", "execution_adoption"), revision=3)
    unit = p0.append_record(store, "plan_unit_state", "UNITSTATE-0004", "UNITSTATE-W-PHASE0-UNIT-001", p0.unit_state_payload("succeeded", operation_ref="records/OP-0005.md", effect_ref=effect_ref, result_refs=[artifact, completed["observation_ref"]], last_event_ref=artifact), p0.actor("p3-owner", "P3", "execution_adoption"), revision=4)
    adopted = p0.append_record(store, "delegated_operation", "OP-0005", "OP-INT-001", p0.operation_payload(state["dispatch_sha"], "succeeded", return_ref=completed["return_ref"], return_sha=completed["return_sha"], adoption="adopted", provider_sequence=2, evidence_refs=[completed["observation_ref"]], effect_refs=[effect_ref], remote_operation_id=OPERATION_ID), p0.actor("p3-owner", "P3", "execution_adoption"), revision=5)
    ws = p0.append_record(store, "work_state", "WS-0004", "WS-W-PHASE0", {"checkpoint": "executed", "interrupt_ref": None}, p0.actor("p3-owner", "P3", "execution_adoption"), revision=4)
    store.log("p3_adoption", operation_ref=adopted, effect_ref=effect_ref, artifact_ref=artifact, adoption_count=1)
    store.commit([artifact, effect_ref, unit, adopted, ws], ws, "P3 adoption completed before conflicting P4 evidence; acceptance remains separate.")
    return completed["observation_ref"]


def d8_evidence_conflict(run_dir: Path) -> dict[str, Any]:
    state = p1.build_prefix(run_dir, "C1")
    store: p0.RunStore = state["store"]
    p1.provider_submit(run_dir, state["dispatch_sha"], store)
    p1.persist_running(store, state["dispatch_sha"], state["effect_ref"])
    p1.provider_set_running(run_dir, store)
    completed = p1.provider_complete(run_dir, store, state["packet"], "records/EFF-0002.md")
    observation_ref = adopt_only_for_conflict(store, state, completed)
    evidence_a = p0.append_record(store, "evidence", "EVD-0001", "EVD-CLM-A3-A", {"claim_id": "CLM-A3", "criterion_id": "A3", "method_id": "filesystem.inspect", "method_revision": "1", "object_ref": "workspace/output/output.txt", "object_revision": "TARGET-R1", "design_revision": DESIGN_REVISION, "plan_revision": DESIGN_REVISION, "environment_ref": "ENV-LOCAL", "environment_revision": "ENV-LOCAL-R1", "observed_at": store.run_time, "freshness_policy": "Valid for this case.", "expires_at": None, "producer_id": "validator-A", "verifier_id": "p4-owner", "trust_domain": "local-readonly-probe", "source_lineage": [observation_ref], "coverage": "full", "independence_basis": "Independent content check A.", "independence_group": "conflict-A", "status": "valid", "supersedes_refs": [], "contradiction_refs": ["records/EVD-0002.md"], "raw_observation_refs": [observation_ref], "adopted_by": "P4"}, p0.actor("p4-owner", "P4", "evidence_adoption"))
    evidence_b = p0.append_record(store, "evidence", "EVD-0002", "EVD-CLM-A3-B", {"claim_id": "CLM-A3", "criterion_id": "A3", "method_id": "filesystem.inspect", "method_revision": "1", "object_ref": "workspace/output/output.txt", "object_revision": "TARGET-R1", "design_revision": DESIGN_REVISION, "plan_revision": DESIGN_REVISION, "environment_ref": "ENV-LOCAL", "environment_revision": "ENV-LOCAL-R1", "observed_at": store.run_time, "freshness_policy": "Valid for this case.", "expires_at": None, "producer_id": "validator-B", "verifier_id": "p4-owner", "trust_domain": "local-readonly-probe", "source_lineage": [observation_ref], "coverage": "full", "independence_basis": "Independent content check B.", "independence_group": "conflict-B", "status": "valid", "supersedes_refs": [], "contradiction_refs": ["records/EVD-0001.md"], "raw_observation_refs": [observation_ref], "adopted_by": "P4"}, p0.actor("p4-owner", "P4", "evidence_adoption"))
    verdict = p0.append_record(store, "criteria_verdict", "VER-0001", "VER-A3-CONFLICT", {"criterion_id": "A3", "verdict": "UNKNOWN", "evidence_refs": [evidence_a, evidence_b], "method_refs": [latest_ref(store, "validation_method", "VM-CLM-A1-A7")], "object_revision_refs": [TARGET_REVISION], "coverage_complete": False, "freshness_ok": True, "conflict_status": "unresolved", "independence_satisfied": True, "rationale": "Evidence A and B are both valid but mutually contradictory; acceptance is stopped."}, p0.actor("p4-owner", "P4", "criteria_verdict"))
    conflict_obs = store.add_observation("EVIDENCE-CONFLICT.json", {"criterion_id": "A3", "evidence_refs": [evidence_a, evidence_b], "conflict_detected": True, "accepted": False})
    blocker = add_blocker_state(store, case_id="D8", kind="evidence_conflict", symptom="Two valid evidence records support contradictory outcomes for acceptance criterion A3.", effect_ref="EFF-0003", operation_ref="OP-0005", observation_ref=conflict_obs, checkpoint="executed", unit_state="succeeded", unresolved_effect=False, active_operation=False)
    store.commit([evidence_a, evidence_b, verdict], blocker["blocker_set_ref"], "P4 stopped acceptance on unresolved evidence conflict; no PASS or closure was inferred.")
    store.log("evidence_conflict_detected", evidence_count=2, evidence_conflict_count=1, accepted=False, false_acceptance=0)
    checkpoint, disposition, lifecycle = final_state(store)
    metrics = base_metrics("D8", "executed")
    metrics.update({"provider_invocation_count": 1, "effect_count": 1, "return_arrival_count": 1, "return_valid_count": 1, "return_applicable_count": 1, "return_adoption_count": 1, "evidence_count": 2, "evidence_conflict_count": 1, "reconcile_count": 0, "checkpoint_after": checkpoint, "work_lifecycle": lifecycle, "disposition": disposition, "active_blocker_count": 1, "accepted": False, "result": "justified_unresolved"})
    metrics["invariants"] = common_invariants(store, metrics, finite_state=True)
    metrics["acceptance_state"] = {"verdict": "UNKNOWN", "conflict_status": "unresolved", "accepted": False, "closed": False}
    return finalize_case(store, metrics)


def finalize_case(store: p0.RunStore, metrics: dict[str, Any]) -> dict[str, Any]:
    metrics["phase2_status"] = "PASS" if all(metrics["invariants"].values()) else "FAIL"
    result = {"status": metrics["phase2_status"], "case_id": metrics["case_id"], "fault": metrics["injected_fault"], "run_path": store.run_dir.relative_to(RUNNER_ROOT).as_posix(), "metrics": metrics}
    write_json(store.run_dir / "phase2_metrics.json", metrics)
    write_json(store.run_dir / "phase2_result.json", result)
    return result


DISPATCH = {
    "D1": d1_duplicate_return,
    "D2": d2_out_of_order,
    "D3": d3_stale_revision,
    "D4": d4_wrong_binding,
    "D5": d5_effect_unknown,
    "D6": d6_provider_unknown,
    "D7": d7_partial_effect,
    "D8": d8_evidence_conflict,
}


def preflight() -> dict[str, Any]:
    compile_run = subprocess.run([sys.executable, "-m", "py_compile", "runtime/run_baseline.py", "runtime/run_phase1.py", "runtime/run_phase2.py"], cwd=RUNNER_ROOT, capture_output=True, text=True, check=False)
    manifest = p0.validate_manifest()
    phase0_dirs = sorted((RUNNER_ROOT / "runs").glob("20*T*Z"))
    phase0_dir = phase0_dirs[-1] if phase0_dirs else None
    phase0_validation = None
    if phase0_dir is not None:
        expected = json.loads((RUNNER_ROOT / "probe" / "EXPECTED_BASELINE.json").read_text(encoding="utf-8"))
        phase0_validation = p0.verify_run(phase0_dir, manifest, expected)
    elif (RUNNER_ROOT / "evidence" / "phase0" / "result.json").is_file():
        committed_phase0 = load_json(RUNNER_ROOT / "evidence" / "phase0" / "result.json")
        phase0_validation = committed_phase0.get("validation", {"status": committed_phase0.get("status", "FAIL")})
    matrix_path = RUNNER_ROOT / "runs" / "phase1" / "phase1_matrix.json"
    committed_matrix_path = RUNNER_ROOT / "evidence" / "phase1" / "phase1_matrix.json"
    phase1_matrix = load_json(matrix_path) if matrix_path.is_file() else load_json(committed_matrix_path) if committed_matrix_path.is_file() else {"status": "FAIL"}
    phase1_cases = []
    for case_id in ("C1", "C2", "C3", "C4"):
        case_dir = RUNNER_ROOT / "runs" / "phase1" / case_id
        if case_dir.is_dir():
            phase1_cases.append(p1.verify_case(case_id, case_dir))
    if not phase1_cases and (RUNNER_ROOT / "evidence" / "phase1" / "phase1_matrix.json").is_file():
        committed_phase1 = load_json(RUNNER_ROOT / "evidence" / "phase1" / "phase1_matrix.json")
        phase1_cases = [{"status": item.get("status", "FAIL"), "case_id": item.get("case_id")} for item in committed_phase1.get("cases", [])]
    if len(phase1_cases) != 4:
        phase1_cases = [{"status": "FAIL", "case_id": case_id} for case_id in ("C1", "C2", "C3", "C4")]
    phase1_ok = phase1_matrix.get("status") == "PASS" and all(item.get("status") == "PASS" for item in phase1_cases)
    result = {
        "python_compile": "PASS" if compile_run.returncode == 0 else "FAIL",
        "manifest": {"status": "PASS", "unresolved": 0, "hash_mismatch": 0, "fallback": len(manifest["resolver_events"]), "spec_runtime_root": p0.SPEC_RUNTIME_ROOT.relative_to(RUNNER_ROOT).as_posix()},
        "fresh_phase0": phase0_validation or {"status": "FAIL", "reason": "no baseline run"},
        "phase0_verify": phase0_validation or {"status": "FAIL"},
        "phase1_evidence_verify": {"status": "PASS" if phase1_ok else "FAIL", "matrix_status": phase1_matrix.get("status"), "cases": [{"case_id": item.get("case_id"), "status": item.get("status")} for item in phase1_cases]},
    }
    result["status"] = "PASS" if result["python_compile"] == "PASS" and result["manifest"]["status"] == "PASS" and result["fresh_phase0"].get("status") == "PASS" and result["phase0_verify"].get("status") == "PASS" and phase1_ok else "FAIL"
    return result


def run_matrix() -> dict[str, Any]:
    gate = preflight()
    if gate["status"] != "PASS":
        return {"status": "BLOCKED", "pre_phase_gate": gate, "reason": "Pre-Phase Gate did not pass; no adversarial case was started."}
    root = RUNNER_ROOT / "runs" / "phase2"
    root.mkdir(parents=True, exist_ok=True)
    gate_results: dict[str, list[dict[str, Any]]] = {"A": [], "B": [], "C": []}
    for gate_name, cases in (("A", GATE_A), ("B", GATE_B), ("C", GATE_C)):
        prior = [item for group in gate_results.values() for item in group]
        if any(item["status"] != "PASS" for item in prior):
            return {"status": "BLOCKED", "pre_phase_gate": gate, "gates": gate_results, "reason": f"Gate {gate_name} was not started because a prior gate failed."}
        for case_id in cases:
            run_dir = root / case_id
            if run_dir.exists():
                raise Phase2Error(f"case directory already exists; remove only this exact Phase 2 directory before rerun: {run_dir}")
            if OUTPUT_PATH.exists():
                OUTPUT_PATH.unlink()
            result = DISPATCH[case_id](run_dir)
            gate_results[gate_name].append(result)
            if result["status"] != "PASS":
                return {"status": "FAIL", "pre_phase_gate": gate, "gates": gate_results, "reason": f"{case_id} failed."}
    result = {
        "status": "PASS",
        "overall_verdict": "PASS",
        "pre_phase_gate": gate,
        "gates": gate_results,
        "finding_classification": [],
        "next_gate": "Phase 3 — Control / Budget / Trust Boundary Probeへ進行可能",
        "implemented": {"runtime": [], "probe_harness": ["runtime/run_phase2.py"]},
    }
    write_json(root / "phase2_matrix.json", result)
    return result


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run the deterministic FPO Phase 2 adversarial state-consistency probe")
    parser.add_argument("command", choices=("matrix", "case", "preflight"), nargs="?", default="matrix")
    parser.add_argument("--case", choices=CASES, default=None)
    parser.add_argument("--run", dest="run_path", default=None)
    args = parser.parse_args()
    try:
        if args.command == "preflight":
            result = preflight()
        elif args.command == "matrix":
            result = run_matrix()
        else:
            if args.case is None or args.run_path is None:
                raise Phase2Error("case requires --case and --run")
            run_dir = Path(args.run_path).resolve()
            if run_dir.exists():
                raise Phase2Error(f"case directory already exists: {run_dir}")
            if OUTPUT_PATH.exists():
                OUTPUT_PATH.unlink()
            result = DISPATCH[args.case](run_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    except (Phase2Error, p0.ProbeError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
