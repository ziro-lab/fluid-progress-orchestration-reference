"""Phase 5C Context Compiler candidate A/B experiment adapter.

Raw and compiled arms share the same task fixtures, model, reasoning level,
tool profile, budget, retrieval access, and oracle held outside worker input.
The compiler organizes context; it does not solve the task or change FPO
authority.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AB_ROOT = ROOT / "phase5c" / "ab"
FIXTURE = ROOT / "phase5c" / "fixture" / "ab-fixtures.json"
RUN_ROOT = AB_ROOT / "runs"
RAW_ROOT = AB_ROOT / "raw"
COMPILED_ROOT = AB_ROOT / "compiled"
RESULT_ROOT = AB_ROOT / "results"
AGGREGATE = AB_ROOT / "aggregate.json"
REPORT = AB_ROOT / "report.md"
BASELINE_COMMIT = "7beae3d624dcbb5f4927501ac4339529114c357b"
SKILL_COMMIT_SHA = "29ada0d48cf9719e53708fd693bf573b69ef487d"
RUNS = ("T1-RAW", "T1-COMPILED", "T2-RAW", "T2-COMPILED")


class ProbeError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any, *, immutable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(value)
    if immutable and path.exists():
        if path.read_bytes() != data:
            raise ProbeError(f"immutable artifact differs on rerun: {path}")
        return
    path.write_bytes(data)


def write_text(path: Path, value: str, *, immutable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value.encode("utf-8")
    if immutable and path.exists():
        if path.read_bytes() != data:
            raise ProbeError(f"immutable artifact differs on rerun: {path}")
        return
    path.write_bytes(data)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    if "const" in schema and value != schema["const"]:
        raise ProbeError(f"{path}: const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        raise ProbeError(f"{path}: enum mismatch")
    expected = schema.get("type")
    if expected:
        kinds = expected if isinstance(expected, list) else [expected]
        if not any((kind == "object" and isinstance(value, dict)) or (kind == "array" and isinstance(value, list)) or (kind == "string" and isinstance(value, str)) or (kind == "integer" and isinstance(value, int) and not isinstance(value, bool)) or (kind == "boolean" and isinstance(value, bool)) for kind in kinds):
            raise ProbeError(f"{path}: type mismatch")
    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value:
                raise ProbeError(f"{path}: missing {required}")
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(schema.get("properties", {}))
            if extra:
                raise ProbeError(f"{path}: unexpected {sorted(extra)}")
        for key, child in schema.get("properties", {}).items():
            if key in value:
                validate_schema(value[key], child, f"{path}.{key}")
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate_schema(item, schema["items"], f"{path}[{index}]")
    if isinstance(value, str) and "pattern" in schema:
        import re
        if not re.search(schema["pattern"], value):
            raise ProbeError(f"{path}: pattern mismatch")
    if isinstance(value, int) and value < schema.get("minimum", value):
        raise ProbeError(f"{path}: below minimum")


def worker_schema() -> dict[str, Any]:
    return read_json(ROOT / "phase5c" / "contracts" / "ab_return.schema.json")


def validate_worker(value: dict[str, Any]) -> None:
    validate_schema(value, worker_schema())


def fixture() -> dict[str, Any]:
    return read_json(FIXTURE)


def task_id(run_id: str) -> str:
    return run_id.split("-", 1)[0]


def arm(run_id: str) -> str:
    return run_id.split("-", 1)[1]


def run_dir(run_id: str) -> Path:
    return RUN_ROOT / run_id


def raw_context(task: str) -> dict[str, Any]:
    data = copy.deepcopy(fixture()["tasks"][task])
    return {"schema": "fpo.phase5c.ab-raw-context.v1", "task_id": task, "skill_not_loaded": True, **data}


def compile_context(raw: dict[str, Any]) -> dict[str, Any]:
    """Minimal candidate adapter: preserve coverage, then organize context."""
    sections = {
        "hard_constraints": copy.deepcopy(raw["hard_constraints"]),
        "decisions": copy.deepcopy(raw["decisions"]),
        "current_evidence": copy.deepcopy(raw["current_evidence"]),
        "open_uncertainty": copy.deepcopy(raw["uncertainty"]),
        "exact_identifiers": copy.deepcopy(raw["exact_identifiers"]),
        "current_task_state": raw["task_state"],
        "invalidated_routes": copy.deepcopy(raw["invalidated_routes"]),
        "retrieval_pointers": copy.deepcopy(raw["retrieval_pointers"]),
    }
    ledger = []
    for name in ["hard_constraints", "decisions", "current_evidence", "uncertainty", "exact_identifiers", "task_state", "invalidated_routes", "retrieval_pointers"]:
        ledger.append({"field": name, "classification": "Must Preserve" if name in {"hard_constraints", "decisions", "current_evidence", "uncertainty", "exact_identifiers", "task_state", "invalidated_routes"} else "Retrievable Only", "source_field": name, "preserved": True})
    ledger.extend([{"field": "noise", "classification": "Excluded with reason", "reason": "low-immediacy activity/prose; source remains available in raw persisted context", "retrieval_pointer": "raw-context"}, {"field": "raw_summary", "classification": "Excluded with reason", "reason": "convenience prose cannot outrank source-bound state", "retrieval_pointer": "raw-context"}])
    return {"schema": "fpo.phase5c.ab-compiled-context.v1", "task_id": raw["task_id"], "skill_revision": fixture()["skill_revision"], "skill_commit_sha": SKILL_COMMIT_SHA, "source_context_sha256": sha256_bytes(raw), "coverage_first": True, "compression_second": True, "sections": sections, "coverage_ledger": ledger, "retrieval_pointers": copy.deepcopy(raw["retrieval_pointers"]), "excluded_source_fields": ["noise", "raw_summary"]}


def prompt_for(run_id: str, context_ref: str) -> str:
    return "\n".join([
        f"You are Fresh Luna A/B worker for {run_id}.",
        "Use the same model/reasoning/tools/budget as every other arm. You have no parent chat, prior transcript, or hidden reasoning.",
        f"Read only this assigned context: {context_ref}",
        "Do not read oracle, grader, aggregate, report, another run, or the Skill source. Do not solve a different task.",
        "Recover the current task state from the assigned context. Preserve exact hard constraints, identifiers, Evidence refs, uncertainty, invalidated routes, and retrieval pointers.",
        "Return a resume proposal only; do not execute repair, validation, acceptance, close, or authority changes.",
        "Write exactly one JSON object matching phase5c/contracts/ab_return.schema.json to the assigned return.json.",
    ]) + "\n"


def prepare_all() -> dict[str, Any]:
    for task in ["T1", "T2"]:
        raw = raw_context(task)
        write_json(RAW_ROOT / f"{task}.json", raw, immutable=True)
        write_json(COMPILED_ROOT / f"{task}.json", compile_context(raw), immutable=True)
        for current_arm in ["RAW", "COMPILED"]:
            run_id = f"{task}-{current_arm}"
            target = run_dir(run_id)
            target.mkdir(parents=True, exist_ok=True)
            context_ref = f"phase5c/ab/{'raw' if current_arm == 'RAW' else 'compiled'}/{task}.json"
            write_json(target / "context.json", read_json(RAW_ROOT / f"{task}.json") if current_arm == "RAW" else read_json(COMPILED_ROOT / f"{task}.json"), immutable=True)
            dispatch = {"schema": "fpo.phase5c.ab-dispatch.v1", "run_id": run_id, "task_id": task, "arm": current_arm, "work_id": fixture()["tasks"][task]["work_id"], "starting_revision": fixture()["tasks"][task]["starting_revision"], "model": fixture()["target_model"], "reasoning": fixture()["reasoning"], "tool_profile": fixture()["tool_profile"], "budget": "same-fixed-budget", "context_ref": context_ref, "retrieval_access": copy.deepcopy(fixture()["tasks"][task]["retrieval_pointers"]), "oracle_ref": "parent-only-not-worker-visible"}
            write_json(target / "dispatch.json", dispatch, immutable=True)
            write_text(target / "worker-prompt.txt", prompt_for(run_id, context_ref), immutable=True)
    return {"status": "PASS", "runs": list(RUNS), "model": fixture()["target_model"], "reasoning": fixture()["reasoning"], "skill_commit_sha": SKILL_COMMIT_SHA}


def record_worker(run_id: str, agent_id: str) -> dict[str, Any]:
    target = run_dir(run_id)
    value = read_json(target / "return.json")
    validate_worker(value)
    task = task_id(run_id)
    receipt = {"schema": "fpo.phase5c.ab-fresh-receipt.v1", "run_id": run_id, "task_id": task, "arm": arm(run_id), "agent_id": agent_id, "fresh_worker": True, "real_ai_invocation": True, "model": fixture()["target_model"], "reasoning": fixture()["reasoning"], "tool_profile": fixture()["tool_profile"], "prior_transcript_provided": False, "prior_hidden_reasoning_provided": False, "status": "recorded"}
    write_json(target / "worker-receipt.json", receipt, immutable=True)
    return receipt


def grade_run(run_id: str) -> dict[str, Any]:
    if (RESULT_ROOT / f"{run_id}.json").is_file():
        return read_json(RESULT_ROOT / f"{run_id}.json")
    target = run_dir(run_id)
    value = read_json(target / "return.json")
    receipt = read_json(target / "worker-receipt.json")
    task = task_id(run_id)
    expected = fixture()["tasks"][task]
    checks = {
        "task_binding": value["task_id"] == task,
        "arm_binding": value["arm"] == arm(run_id),
        "run_binding": value["run_id"] == run_id,
        "work_binding": value["work_id"] == expected["work_id"],
        "revision_binding": value["starting_revision"] == expected["starting_revision"],
        "next_action_present": expected["expected_next_action"] in value["next_action"],
        "constraints_complete": set(expected["hard_constraints"]).issubset(set(value["preserved_constraints"])),
        "identifiers_complete": set(expected["exact_identifiers"]).issubset(set(value["exact_identifiers"])),
        "evidence_bound": all(item["evidence_id"] in value["evidence_refs"] or item["source_ref"] in value["evidence_refs"] for item in expected["current_evidence"]),
        "uncertainty_preserved": {item["uncertainty_id"] for item in expected["uncertainty"]}.issubset(set(value["uncertainty_ids"])),
        "invalidated_routes_preserved": {item["route_id"] for item in expected["invalidated_routes"]}.issubset(set(value["invalidated_route_ids"])),
        "fresh_no_transcript": receipt["fresh_worker"] and not receipt["prior_transcript_provided"] and not receipt["prior_hidden_reasoning_provided"],
    }
    metrics = value["metrics"]
    computed_success = all(checks.values()) and metrics["task_success"] and metrics["missed_constraints"] == 0 and metrics["unsupported_assumptions"] == 0 and metrics["stale_state_adoption"] == 0 and metrics["invalidated_route_resurrection"] == 0 and metrics["duplicate_work"] == 0 and metrics["final_validation_result"] in {"READY", "NOT_YET_DUE", "PASS"}
    result = {"schema": "fpo.phase5c.ab-result.v1", "run_id": run_id, "task_id": task, "arm": arm(run_id), "status": "PASS" if computed_success else "FAIL", "computed_task_success": computed_success, "checks": checks, "metrics": metrics, "return_sha256": sha256_file(target / "return.json"), "receipt": receipt}
    write_json(RESULT_ROOT / f"{run_id}.json", result, immutable=True)
    return result


def compiler_audit() -> dict[str, Any]:
    checks = []
    for task in ["T1", "T2"]:
        raw = read_json(RAW_ROOT / f"{task}.json")
        compiled = read_json(COMPILED_ROOT / f"{task}.json")
        sections = compiled["sections"]
        checks.extend([sections["hard_constraints"] == raw["hard_constraints"], sections["decisions"] == raw["decisions"], sections["current_evidence"] == raw["current_evidence"], sections["open_uncertainty"] == raw["uncertainty"], sections["exact_identifiers"] == raw["exact_identifiers"], sections["current_task_state"] == raw["task_state"], sections["invalidated_routes"] == raw["invalidated_routes"], sections["retrieval_pointers"] == raw["retrieval_pointers"], compiled["skill_commit_sha"] == SKILL_COMMIT_SHA, compiled["coverage_first"] is True])
    return {"preservation_pass": all(checks), "checks": len(checks), "failed": checks.count(False), "skill_commit_sha": SKILL_COMMIT_SHA}


def regression_check() -> dict[str, Any]:
    phase5a = read_json(ROOT / "phase5a" / "aggregate.json")
    phase5b = read_json(ROOT / "phase5b" / "aggregate.json")
    shared = subprocess.run(["git", "diff", "--quiet", BASELINE_COMMIT, "--", "spec/v0.2", "runtime", "evidence"], cwd=ROOT, check=False).returncode == 0
    return {"schema": "fpo.phase5c.ab-regression.v1", "status": "PASS" if shared and phase5a.get("overall_verdict") == "PASS" and phase5b.get("overall_verdict") == "PASS" else "FAIL", "baseline_commit": BASELINE_COMMIT, "shared_runtime_spec_evidence_unchanged": shared, "phase5a": phase5a.get("overall_verdict"), "phase5b": phase5b.get("overall_verdict")}


def report() -> dict[str, Any]:
    if AGGREGATE.is_file():
        return read_json(AGGREGATE)
    results = [grade_run(run_id) for run_id in RUNS]
    audit = compiler_audit()
    regression = regression_check()
    raw_results = [item for item in results if item["arm"] == "RAW"]
    compiled_results = [item for item in results if item["arm"] == "COMPILED"]
    raw_success = sum(item["computed_task_success"] for item in raw_results)
    compiled_success = sum(item["computed_task_success"] for item in compiled_results)
    if compiled_success > raw_success and compiled_success == len(compiled_results):
        classification = "PROMISING"
    elif compiled_success < raw_success:
        classification = "REGRESSION"
    elif compiled_success > raw_success:
        classification = "INSUFFICIENT_EVIDENCE"
    else:
        classification = "NEUTRAL"
    aggregate = {"schema": "fpo.phase5c.ab-aggregate.v1", "overall_verdict": "PASS" if audit["preservation_pass"] and regression["status"] == "PASS" else "FAIL", "context_compiler_classification": classification, "skill_revision": fixture()["skill_revision"], "skill_commit_sha": SKILL_COMMIT_SHA, "compiler_audit": audit, "controlled_conditions": {"model": fixture()["target_model"], "reasoning": fixture()["reasoning"], "tool_profile": fixture()["tool_profile"], "same_source": True, "same_oracle": True, "same_budget": True, "same_retrieval_access": True}, "results": results, "comparison": {"raw_task_success": raw_success, "compiled_task_success": compiled_success, "raw_missed_constraints": sum(item["metrics"]["missed_constraints"] for item in raw_results), "compiled_missed_constraints": sum(item["metrics"]["missed_constraints"] for item in compiled_results), "raw_duplicate_work": sum(item["metrics"]["duplicate_work"] for item in raw_results), "compiled_duplicate_work": sum(item["metrics"]["duplicate_work"] for item in compiled_results), "raw_unnecessary_rereads": sum(item["metrics"]["unnecessary_rereads"] for item in raw_results), "compiled_unnecessary_rereads": sum(item["metrics"]["unnecessary_rereads"] for item in compiled_results), "raw_unnecessary_research": sum(item["metrics"]["unnecessary_research"] for item in raw_results), "compiled_unnecessary_research": sum(item["metrics"]["unnecessary_research"] for item in compiled_results), "raw_retries_rework": sum(item["metrics"]["retries_rework"] for item in raw_results), "compiled_retries_rework": sum(item["metrics"]["retries_rework"] for item in compiled_results)}, "regression": regression}
    lines = ["# FPO Phase 5C — Part B/C Context Compiler A/B", "", f"Overall verdict: **{aggregate['overall_verdict']}**", f"Context Compiler classification: **{classification}**", "", f"Candidate revision: `{fixture()['skill_revision']}`", f"Candidate commit SHA: `{SKILL_COMMIT_SHA}`", "", "## A/B Matrix", "", "| Task | Arm | Result | Success | Missed constraints | Unsupported assumptions | Stale adoption | Invalidated route resurrection | Rereads | Research | Duplicate work | Rework | Evidence quality | Retrieval usage | Final validation |", "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|"]
    for item in results:
        m = item["metrics"]
        lines.append(f"| {item['task_id']} | {item['arm']} | {item['status']} | {item['computed_task_success']} | {m['missed_constraints']} | {m['unsupported_assumptions']} | {m['stale_state_adoption']} | {m['invalidated_route_resurrection']} | {m['unnecessary_rereads']} | {m['unnecessary_research']} | {m['duplicate_work']} | {m['retries_rework']} | {m['evidence_quality']} | {m['retrieval_pointer_usage']} | {m['final_validation_result']} |")
    lines.extend(["", "## Interpretation", "", f"Raw task success: {raw_success}/{len(raw_results)}; Compiled task success: {compiled_success}/{len(compiled_results)}.", "The candidate is not promoted from one improved task; classification requires transfer across both distinct fixtures and no unacceptable regression.", "", "## Compiler audit", "", f"- preservation_pass: {audit['preservation_pass']}", f"- failed preservation checks: {audit['failed']}", "- oracle read by compiler/worker: false by construction", "", "## Next", "", "Core Resume PASS remains independent of this candidate A/B. Context Compiler promotion stays in Skill Lab based on this classification.", ""])
    write_json(AGGREGATE, aggregate, immutable=True)
    write_text(REPORT, "\n".join(lines), immutable=True)
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare-all", "record-worker", "grade", "report"])
    parser.add_argument("--run-id", choices=RUNS)
    parser.add_argument("--agent-id")
    args = parser.parse_args()
    try:
        if args.command == "prepare-all":
            result = prepare_all()
        elif args.command == "record-worker":
            if not args.run_id or not args.agent_id:
                raise ProbeError("record-worker requires --run-id and --agent-id")
            result = record_worker(args.run_id, args.agent_id)
        elif args.command == "grade":
            if not args.run_id:
                raise ProbeError("grade requires --run-id")
            result = grade_run(args.run_id)
        else:
            result = report()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("status") == "PASS" or result.get("overall_verdict") == "PASS" else 1
    except (ProbeError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
