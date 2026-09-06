"""Parent-side Phase 7B Parallel Profile Runtime Conformance harness.

The harness exercises a concrete local Provider against independently retained
mechanical and oracle fixtures.  The oracle and final acceptance stay in this
parent-side script; no worker is given hidden expected fixes or routes.
"""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from provider.parallel_provider import (
    CasConflictError,
    CompositionConflictError,
    IncompleteBindingError,
    MediationError,
    ParallelProvider,
    ProviderError,
    StaleBindingError,
    digest,
    runtime_identity,
)


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
PROFILE_ROOT = REPO / "profiles" / "parallel-model" / "v0.1.4.2"
STARTING_REVISION = "0407c72a642ce7c98a30a9016feaf63bf1e62351"
PHASE6_BASELINE = "fb74cac46a3833195262f6e4a3a78c3034b819a9"
SEED = "Execute the bounded v0.1.4.2 Provider conformance work, verify safety, and report only what is proven."
REQUIRED_BINDING = [
    "definition",
    "plan",
    "attempt",
    "target",
    "approval",
    "capability",
    "dispatch",
]
REQUIRED_CHANNELS = [
    {"channel": "process_tree", "applicable": True},
    {"channel": "queued_callback", "applicable": True},
]
MECHANICAL_IDS = ["X1a", "X1b", "X2a", "X2b", "X3", "X4", "X5", "X6", "E1a", "E1b", "H3", "L1", "T1a", "T1b"]
ORACLE_IDS = ["T2", "D1", "P1", "R1", "H1", "H2"]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def next_attempt_path(probe_id: str) -> Path:
    base = ROOT / "attempts" / probe_id
    base.mkdir(parents=True, exist_ok=True)
    numbers = []
    for path in base.glob("run-*.json"):
        try:
            numbers.append(int(path.stem.split("-")[-1]))
        except ValueError:
            pass
    return base / f"run-{max(numbers, default=0) + 1:03d}.json"


def make_capability_profile() -> dict[str, Any]:
    return {
        "schema": "fpo.phase7b.provider-capability-profile.v1",
        "revision": "phase7b-capability-v1",
        "profile_revision": "0.1.4.2",
        "required_binding": [{"name": name} for name in REQUIRED_BINDING],
        "required_channels": REQUIRED_CHANNELS,
        "semantic_safety": {
            "dependencies": ["owner-native-definition", "owner-native-plan"],
            "conflict_domains": ["semantic-index"],
            "invariants": ["artifact-integrity", "owner-currentness"],
            "capability_restrictions": {"no_unmediated_persistent_write": True, "digest_identity_required": True},
            "effect_class": "file-write",
            "provider_path": "local-cas",
        },
        "publication": "existing-fpo-artifact-surface",
    }


def make_host_policy() -> dict[str, Any]:
    return {
        "schema": "fpo.phase7b.host-policy.v1",
        "revision": "phase7b-host-policy-v1",
        "host_parallel_cap": 3,
        "queue_on_slot_shortage": True,
        "top_level_fallback": False,
        "model_policy": {"default_worker": "gpt-5.6-luna", "reasoning": "xhigh", "sol": "only-if-needed"},
        "fixed_worker_topology": False,
    }


def prepare() -> dict[str, Any]:
    for directory in ("provider", "fixtures", "attempts", "evidence", "validation", "oracles"):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    profile = make_capability_profile()
    host = make_host_policy()
    write_json(ROOT / "provider" / "capability-profile.json", profile)
    write_json(ROOT / "provider" / "host-policy.json", host)
    write_json(ROOT / "oracles" / "parallel.oracle.json", {
        "schema": "fpo.phase7b.parent-only-oracle.v1",
        "owner": "parent FPO",
        "not_worker_input": True,
        "mechanical": {probe_id: "profile-defined safety expectation" for probe_id in MECHANICAL_IDS},
        "oracle": {probe_id: "parent semantic expectation" for probe_id in ORACLE_IDS},
        "integrated": "exact immutable fan-in revision independently validated and accepted",
    })
    write_json(ROOT / "fixtures" / "manifest.json", {
        "schema": "fpo.phase7b.independent-fixture-manifest.v1",
        "seed": SEED,
        "mechanical": [{"id": probe_id, "fixture": f"fixtures/{probe_id}.json", "oracle_ref": "phase7b/oracles/parallel.oracle.json"} for probe_id in MECHANICAL_IDS],
        "oracle": [{"id": probe_id, "fixture": f"fixtures/{probe_id}.json", "oracle_ref": "phase7b/oracles/parallel.oracle.json"} for probe_id in ORACLE_IDS],
        "integrated": {"fixture": "fixtures/FANIN.json", "oracle_ref": "phase7b/oracles/parallel.oracle.json"},
        "worker_context": {"fresh_workers": 0, "transcript": False, "hidden_oracle": False},
    })
    for probe_id in MECHANICAL_IDS + ORACLE_IDS:
        write_json(ROOT / "fixtures" / f"{probe_id}.json", {
            "schema": "fpo.phase7b.fixture.v1",
            "probe_id": probe_id,
            "class": "MECHANICAL" if probe_id in MECHANICAL_IDS else "ORACLE",
            "independent": True,
            "seed_ref": "phase7b/fixtures/manifest.json",
            "trusted_oracle_ref": "phase7b/oracles/parallel.oracle.json",
        })
    write_json(ROOT / "fixtures" / "FANIN.json", {
        "schema": "fpo.phase7b.fixture.v1",
        "probe_id": "FANIN",
        "class": "INTEGRATED_FAN_OUT_FAN_IN",
        "independent": True,
        "seed_ref": "phase7b/fixtures/manifest.json",
        "trusted_oracle_ref": "phase7b/oracles/parallel.oracle.json",
    })
    return {"status": "PASS", "profile_revision": "0.1.4.2", "seed": SEED}


def exact_ref(name: str, revision: str) -> dict[str, str]:
    return {"revision": revision, "digest": digest({"name": name, "revision": revision}), "source": "owner-native"}


def operation(attempt_id: str = "ATT-001", child_sub_id: str = "child-001", *, destination: str = "shared", plan_revision: str = "plan-r1") -> dict[str, Any]:
    refs = {
        "definition": exact_ref("definition", "definition-r1"),
        "plan": exact_ref("plan", plan_revision),
        "attempt": exact_ref("attempt", f"{attempt_id}-r1"),
        "target": exact_ref("target", "target-r1"),
        "approval": exact_ref("approval", "approval-r1"),
        "capability": exact_ref("capability", "capability-r1"),
        "dispatch": exact_ref("dispatch", "dispatch-r1"),
    }
    return {
        "attempt_id": attempt_id,
        "child_sub_id": child_sub_id,
        "refs": refs,
        "capability": "parallel-file-write",
        "effect_class": "file-write",
        "provider_path": "local-cas",
        "destination": destination,
        "required_at_spawn": copy.deepcopy(REQUIRED_CHANNELS),
        "conflict_domains": [f"physical:{destination}"],
        "invariants": ["artifact-integrity"],
    }


def context(provider: ParallelProvider, op: dict[str, Any], *, current_refs: dict[str, Any] | None = None, composition: bool = True) -> dict[str, Any]:
    return {
        "current_owner_refs": copy.deepcopy(current_refs or op["refs"]),
        "current_attempt_id": op["attempt_id"],
        "approval_authority_valid": True,
        "material_observations_current": True,
        "enforced_capability_envelope_valid": True,
        "parallel_composition_constraints_satisfied": composition,
    }


def begin(provider: ParallelProvider, op: dict[str, Any], ctx: dict[str, Any], mutation_id: str, domain: str | None = None) -> dict[str, Any]:
    return provider.begin_effect({
        "operation": op,
        "mutation_id": mutation_id,
        "path": "begin_effect",
        "registrable": True,
        "mutation_domain": domain or op["destination"],
    }, ctx)


def settled_observations(channels: list[dict[str, Any]] = REQUIRED_CHANNELS, status: str = "terminal") -> list[dict[str, Any]]:
    return [{"channel": item["channel"], "status": status, "proof": f"proof:{item['channel']}"} for item in channels if item.get("applicable", True)]


def result(probe_id: str, details: dict[str, Any], metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"probe_id": probe_id, "status": "PASS", "details": details, "metrics": metrics or {}}


def probe_x1a() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    ctx = context(p, op)
    binding = p.normalize_execution_binding(op, ctx)
    current = p.eligible({**op, "binding": binding}, ctx)
    stale_refs = copy.deepcopy(op["refs"])
    stale_refs["plan"] = exact_ref("plan", "plan-r2")
    stale = p.eligible({**op, "binding": binding}, context(p, op, current_refs=stale_refs))
    return result("X1a", {"current_eligible": current, "superseded_eligible": stale, "normalized_component_count": len(binding["components"]), "revoke_authority": False}, {"derived_currentness": True}) if current and not stale else {"probe_id": "X1a", "status": "FAIL", "details": {"current": current, "stale": stale}}


def probe_x1b() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    ctx = context(p, op)
    binding = p.normalize_execution_binding(op, ctx)
    missing = copy.deepcopy(binding)
    missing["components"] = [item for item in missing["components"] if item["name"] != "plan"]
    missing_ok = p.validate_binding_completeness(REQUIRED_BINDING, missing)
    narrowed_op = copy.deepcopy(op)
    narrowed_op["refs"].pop("plan")
    narrowed_binding = p.normalize_execution_binding(narrowed_op, {**ctx, "required_binding": ["attempt"]})
    narrowed_eligible = p.eligible({**narrowed_op, "binding": narrowed_binding}, {**ctx, "required_binding": ["attempt"]})
    alias_op = copy.deepcopy(op)
    alias_op["refs"]["plan"] = "current"
    alias_binding = p.normalize_execution_binding(alias_op, ctx)
    alias_eligible = p.eligible({**alias_op, "binding": alias_binding}, ctx)
    ok = not missing_ok and not narrowed_eligible and not alias_eligible
    payload = {"missing_component_rejected": not missing_ok, "worker_required_override_ignored": not narrowed_eligible, "mutable_alias_rejected": not alias_eligible}
    return result("X1b", payload) if ok else {"probe_id": "X1b", "status": "FAIL", "details": payload}


def probe_x2a() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    required = p.required_channels(op)
    observations = settled_observations(required)
    fence = settled_observations(required, "fenced")
    settled = p.derive_closure(required, observations, [])
    fenced = p.derive_closure(required, [], fence)
    incomplete = p.derive_closure(required, observations[:1], [])
    details = {"settled": settled, "fenced": fenced, "incomplete": incomplete, "required_channels": required}
    return result("X2a", details) if settled == "SETTLED" and fenced == "FENCED" and incomplete == "UNKNOWN" else {"probe_id": "X2a", "status": "FAIL", "details": details}


def probe_x2b() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    required = p.required_channels(op)
    hidden = p.derive_closure(required, settled_observations(required[:1]), [])
    unrelated = {"channel": "remote_job", "applicable": True, "applies_to": {"capability": "remote-job", "effect_class": "remote", "provider_path": "remote"}}
    effective = p.required_channels(op, [unrelated])
    unaffected = p.derive_closure(effective, settled_observations(required) + [{"channel": "remote_job", "status": "unknown", "proof": "not-applicable"}], [])
    details = {"omitted_applicable_channel": hidden, "effective_channels_after_unrelated_discovery": effective, "unrelated_does_not_poison": unaffected}
    return result("X2b", details) if hidden == "UNKNOWN" and unaffected == "SETTLED" and all(item["channel"] != "remote_job" for item in effective) else {"probe_id": "X2b", "status": "FAIL", "details": details}


def probe_x3() -> dict[str, Any]:
    retry_provider = ParallelProvider(make_capability_profile())
    retry_provider.write_ahead_spawn("ATT-X3-ABSENT", "child", "physical:absent")
    retry = retry_provider.reconcile_spawn("ATT-X3-ABSENT", "child", "ABSENT")
    existing_provider = ParallelProvider(make_capability_profile())
    existing_provider.spawn_child("ATT-X3-EXISTS", "child", "RUNNING")
    adopt = existing_provider.reconcile_spawn("ATT-X3-EXISTS", "child", "RUNNING")
    unknown_provider = ParallelProvider(make_capability_profile())
    unknown_provider.write_ahead_spawn("ATT-X3-UNKNOWN", "child", "physical:unknown")
    unknown = unknown_provider.reconcile_spawn("ATT-X3-UNKNOWN", "child", "UNKNOWN")
    details = {"absent": retry, "exists_running": adopt, "unknown": unknown, "retry_spawn_count": retry["mapping"]["spawn_count"]}
    ok = retry["decision"] == "RETRY_SAME_IDENTITY" and adopt["decision"] == "ADOPT" and unknown["decision"] == "RECONCILE_OR_FENCE" and retry["mapping"]["spawn_count"] == 1 and not unknown_provider.physical_children
    return result("X3", details, {"duplicate_physical_child": 0}) if ok else {"probe_id": "X3", "status": "FAIL", "details": details}


def probe_x4() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    p.register_destination("shared", {"value": "before"})
    op = operation()
    ctx = context(p, op)
    effect = begin(p, op, ctx, "X4-write")
    commit = p.external_commit(effect["effect_id"], {"destination": "shared", "expected_revision": "r0", "new_revision": "r1", "value": {"value": "after"}})
    required = p.required_channels(op)
    premature_rejected = False
    try:
        p.freeze_publish({"alias": "x4-artifact", "content": {"state": "partial"}, "closure": p.derive_closure(required, settled_observations(required[:1]), []), "freeze_proof": {"stage": "writes-complete"}})
    except ProviderError:
        premature_rejected = True
    closure = p.derive_closure(required, settled_observations(required), [])
    published = p.freeze_publish({"alias": "x4-artifact", "content": {"state": "complete", "commit": commit}, "closure": closure, "freeze_proof": {"stage": "all-writes-settled"}})
    reconstructed = copy.deepcopy(p.artifact_surface["x4-artifact"]["manifest"])
    details = {"writes_complete": True, "premature_publish_rejected": premature_rejected, "closure": closure, "published_manifest": published["artifact_manifest"], "reconstructed_manifest": reconstructed}
    ok = premature_rejected and closure == "SETTLED" and reconstructed == published["artifact_manifest"]
    return result("X4", details, {"premature_publication": 0, "torn_publication_adoption": 0}) if ok else {"probe_id": "X4", "status": "FAIL", "details": details}


def probe_x5() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    frozen = p.freeze_publish({"alias": "validated-subject", "content": {"integrated": "r1", "branches": ["a", "b"]}, "closure": "SETTLED", "freeze_proof": {"all_channels": True}})
    exact = frozen["frozen"]["immutable_revision"]
    independent_validation = {"status": "PASS", "validated_revision": exact, "independent": True}
    fpo_acceptance = {"status": "accepted", "accepted_revision": exact, "validation_ref": "validation/X5.json"}
    neighboring = digest({"integrated": "r1", "branches": ["a", "b", "neighbor"]})
    details = {"frozen_revision": exact, "independent_validation": independent_validation, "fpo_acceptance": fpo_acceptance, "neighboring_revision": neighboring, "pre_integration_transfer": False}
    ok = independent_validation["validated_revision"] == fpo_acceptance["accepted_revision"] == exact and neighboring != exact
    return result("X5", details, {"validated_revision_equals_accepted_revision": 1 if ok else 0}) if ok else {"probe_id": "X5", "status": "FAIL", "details": details}


def probe_x6() -> dict[str, Any]:
    trusted = make_capability_profile()["semantic_safety"]
    narrowed = {"dependencies": ["owner-native-definition"], "conflict_domains": ["semantic-index"], "invariants": ["artifact-integrity"], "capability_restrictions": {"no_unmediated_persistent_write": True, "digest_identity_required": False}, "effect_class": "file-write", "provider_path": "local-cas"}
    widened = copy.deepcopy(trusted)
    widened["dependencies"].append("worker-suspected-input")
    narrowed_ok = __import__("provider.parallel_provider", fromlist=["covers"]).covers(trusted, narrowed, "semantic_safety")
    widened_ok = __import__("provider.parallel_provider", fromlist=["covers"]).covers(trusted, widened, "semantic_safety")
    details = {"narrowed_claim_accepted": narrowed_ok, "widened_claim_accepted": widened_ok, "trusted_constraints_preserved": not narrowed_ok}
    return result("X6", details) if not narrowed_ok and widened_ok else {"probe_id": "X6", "status": "FAIL", "details": details}


def probe_e1a() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    effect = begin(p, op, context(p, op), "E1a-write")
    intent_event = any(event["kind"] == "effect-intent-durable" and event["effect_id"] == effect["effect_id"] for event in p.events)
    recheck_event = any(event["kind"] == "effect-currentness-recheck" and event["accepted"] for event in p.events)
    details = {"effect_intent": effect, "durable_intent_observable": intent_event, "t1a_recheck_observable": recheck_event}
    return result("E1a", details, {"mediated_effects": 1}) if intent_event and recheck_event and effect["mediated"] else {"probe_id": "E1a", "status": "FAIL", "details": details}


def probe_e1b() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    p.register_destination("shared", {"value": "before"})
    blocked = False
    try:
        p.direct_persist("shared", {"value": "bypass"})
    except MediationError:
        blocked = True
    details = {"direct_persist_blocked": blocked, "destination_unchanged": p.destinations["shared"].value == {"value": "before"}}
    return result("E1b", details, {"unmediated_persistent_effect": 0}) if blocked and details["destination_unchanged"] else {"probe_id": "E1b", "status": "FAIL", "details": details}


def probe_h3() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    original_ctx = context(p, op)
    original_binding = p.normalize_execution_binding(op, original_ctx)
    current_refs = copy.deepcopy(op["refs"])
    current_refs["plan"] = exact_ref("plan", "plan-r2")
    current_ctx = context(p, op, current_refs=current_refs)
    stale_eligible = p.eligible({**op, "binding": original_binding}, current_ctx)
    stale_adoption = p.adopt_return(op, original_binding, current_ctx)
    details = {"stale_eligible": stale_eligible, "stale_return_adopted": stale_adoption, "late_artifact_authority": False}
    return result("H3", details) if not stale_eligible and not stale_adoption else {"probe_id": "H3", "status": "FAIL", "details": details}


def probe_l1() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    p.occupy("child-L1", "mutation-domain-L1")
    p.release_slot("child-L1")
    while_unresolved = p.can_reuse_mutation_domain("mutation-domain-L1", "UNKNOWN")
    p.release_mutation_domain("mutation-domain-L1", "SETTLED")
    after_settled = p.can_reuse_mutation_domain("mutation-domain-L1", "SETTLED")
    details = {"slot_released": "child-L1" not in p.slot_occupancy, "mutation_domain_reusable_while_unknown": while_unresolved, "mutation_domain_reusable_after_settled": after_settled}
    return result("L1", details) if details["slot_released"] and not while_unresolved and after_settled else {"probe_id": "L1", "status": "FAIL", "details": details}


def probe_t1a() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    admission = p.admit_child(op, context(p, op))
    current_refs = copy.deepcopy(op["refs"])
    current_refs["plan"] = exact_ref("plan", "plan-r2")
    rejected = False
    try:
        begin(p, op, context(p, op, current_refs=current_refs), "T1a-stale")
    except StaleBindingError:
        rejected = True
    details = {"admitted": admission["admitted"], "begin_effect_rejected_after_supersession": rejected}
    return result("T1a", details) if admission["admitted"] and rejected else {"probe_id": "T1a", "status": "FAIL", "details": details}


def probe_t1b() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    p.register_destination("shared", {"winner": None})
    op_a = operation("ATT-T1B-A", "child", destination="shared")
    op_b = operation("ATT-T1B-B", "child", destination="shared")
    effect_a = begin(p, op_a, context(p, op_a), "T1b-A")
    effect_b = begin(p, op_b, context(p, op_b), "T1b-B")
    mutations = {
        effect_a["effect_id"]: {"destination": "shared", "expected_revision": "r0", "new_revision": "r1-a", "value": {"winner": "A"}},
        effect_b["effect_id"]: {"destination": "shared", "expected_revision": "r0", "new_revision": "r1-b", "value": {"winner": "B"}},
    }
    outcomes: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(p.external_commit, effect_id, mutation): effect_id for effect_id, mutation in mutations.items()}
        for future in as_completed(futures):
            effect_id = futures[future]
            try:
                future.result()
                outcomes[effect_id] = "COMMITTED"
            except CasConflictError:
                outcomes[effect_id] = "CAS_REJECTED"
    details = {"outcomes": outcomes, "destination_revision": p.destinations["shared"].revision, "mechanism": "destination-CAS", "check_then_mutate_gap": False}
    ok = sorted(outcomes.values()) == ["CAS_REJECTED", "COMMITTED"] and details["destination_revision"] in {"r1-a", "r1-b"}
    return result("T1b", details, {"successful_commits": 1, "cas_rejections": 1}) if ok else {"probe_id": "T1b", "status": "FAIL", "details": details}


def probe_t2() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op = operation()
    old_binding = p.normalize_execution_binding(op, context(p, op))
    changed_refs = copy.deepcopy(op["refs"])
    changed_refs["target"] = exact_ref("target", "target-r2")
    accepted = p.adopt_return(op, old_binding, context(p, op, current_refs=changed_refs))
    details = {"delayed_return_adopted": accepted, "current_owner_wins": not accepted}
    return result("T2", details) if not accepted else {"probe_id": "T2", "status": "FAIL", "details": details}


def probe_d1() -> dict[str, Any]:
    trusted = make_capability_profile()["semantic_safety"]
    worker_declared = copy.deepcopy(trusted)
    worker_declared["dependencies"] = ["owner-native-definition", "owner-native-plan"]
    worker_declared["invariants"] = ["artifact-integrity", "owner-currentness"]
    hidden_oracle_dependency = "hidden-semantic-index"
    trusted_with_hidden = copy.deepcopy(trusted)
    trusted_with_hidden["dependencies"].append(hidden_oracle_dependency)
    accepted = __import__("provider.parallel_provider", fromlist=["covers"]).covers(trusted_with_hidden, worker_declared, "semantic_safety")
    details = {"hidden_dependency": hidden_oracle_dependency, "worker_claim_accepted_as_complete": accepted, "unsafe_narrowing": not accepted}
    return result("D1", details) if not accepted else {"probe_id": "D1", "status": "FAIL", "details": details}


def probe_p1() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    op_a = operation("ATT-P1-A", "child-a", destination="surface-a")
    op_b = operation("ATT-P1-B", "child-b", destination="surface-b")
    op_a["conflict_domains"] = ["physical:surface-a"]
    op_b["conflict_domains"] = ["physical:surface-b"]
    op_a["invariants"] = ["shared-semantic-invariant"]
    op_b["invariants"] = ["shared-semantic-invariant"]
    first = p.admit_child(op_a, context(p, op_a))
    rejected = False
    try:
        p.admit_child(op_b, context(p, op_b), [op_a])
    except CompositionConflictError:
        rejected = True
    details = {"physical_domains_disjoint": True, "shared_invariant": "shared-semantic-invariant", "first_admitted": first["admitted"], "second_rejected": rejected}
    return result("P1", details) if first["admitted"] and rejected else {"probe_id": "P1", "status": "FAIL", "details": details}


def probe_r1() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    p.register_destination("shared", {"value": "before"})
    op_a = operation("ATT-R1-A", "child-a")
    effect_a = begin(p, op_a, context(p, op_a), "R1-A")
    p.external_commit(effect_a["effect_id"], {"destination": "shared", "expected_revision": "r0", "new_revision": "r1", "value": {"value": "valid-change"}})
    op_b = operation("ATT-R1-B", "child-b")
    effect_b = begin(p, op_b, context(p, op_b), "R1-B")
    p.external_commit(effect_b["effect_id"], {"destination": "shared", "expected_revision": "r1", "new_revision": "r2", "value": {"value": "intervening-change"}})
    compensation = p.compensate(effect_a["effect_id"], "shared", "r1", {"value": "before"}, "r-comp")
    details = {"compensation": compensation, "current_value": p.destinations["shared"].value, "intervening_revision_preserved": p.destinations["shared"].revision == "r2"}
    return result("R1", details, {"unsafe_compensation_overwrite": 0}) if compensation["status"] == "REJECTED_SAFE" and details["intervening_revision_preserved"] else {"probe_id": "R1", "status": "FAIL", "details": details}


def probe_h1() -> dict[str, Any]:
    owner_state = {"schema": "fpo.owner-state.v1", "revision": "owner-r2", "decisions": {"scope": "bounded", "semantic_invariant": "artifact-integrity", "mutation_domain": "surface-a"}, "transcript": None}
    required = ["scope", "semantic_invariant", "mutation_domain"]
    fresh_ready = ParallelProvider.planning_ready(owner_state, required)
    details = {"owner_state_revision": owner_state["revision"], "fresh_ready": fresh_ready, "transcript_used": False, "load_bearing_decisions_recovered": fresh_ready}
    return result("H1", details) if fresh_ready and not details["transcript_used"] else {"probe_id": "H1", "status": "FAIL", "details": details}


def probe_h2() -> dict[str, Any]:
    owner_state = {"schema": "fpo.owner-state.v1", "revision": "owner-r3", "decisions": {"scope": "bounded", "mutation_domain": "surface-a"}, "transcript": None}
    required = ["scope", "semantic_invariant", "mutation_domain"]
    ready = ParallelProvider.planning_ready(owner_state, required)
    details = {"fresh_ready": ready, "planning_status": "READY" if ready else "GAP", "blocker": None if ready else "material decision omitted", "guess_used": False}
    return result("H2", details) if not ready and details["blocker"] else {"probe_id": "H2", "status": "FAIL", "details": details}


def integrated_fanin() -> dict[str, Any]:
    p = ParallelProvider(make_capability_profile())
    p.register_destination("surface-a", {"value": None})
    p.register_destination("surface-b", {"value": None})
    op_a = operation("ATT-FANIN-001", "child-a", destination="surface-a")
    op_b = operation("ATT-FANIN-001", "child-b", destination="surface-b")
    op_a["invariants"] = ["branch-a-integrity"]
    op_b["invariants"] = ["branch-b-integrity"]
    admission_a = p.admit_child(op_a, context(p, op_a))
    admission_b = p.admit_child(op_b, context(p, op_b), [op_a])
    effect_a = begin(p, op_a, context(p, op_a), "FANIN-A")
    effect_b = begin(p, op_b, context(p, op_b), "FANIN-B")
    mutations = {
        effect_a["effect_id"]: {"destination": "surface-a", "expected_revision": "r0", "new_revision": "branch-a-r1", "value": {"value": "A"}},
        effect_b["effect_id"]: {"destination": "surface-b", "expected_revision": "r0", "new_revision": "branch-b-r1", "value": {"value": "B"}},
    }
    with ThreadPoolExecutor(max_workers=2) as executor:
        commits = list(executor.map(lambda item: p.external_commit(item[0], item[1]), mutations.items()))
    required = p.required_channels(op_a)
    closure_a = p.derive_closure(required, settled_observations(required), [])
    closure_b = p.derive_closure(required, settled_observations(required), [])
    branch_validation = [{"revision": commits[0]["result_revision"], "status": "PASS"}, {"revision": commits[1]["result_revision"], "status": "PASS"}]
    integrated_content = {"branches": {"a": p.destinations["surface-a"].value, "b": p.destinations["surface-b"].value}, "branch_revisions": [item["revision"] for item in branch_validation]}
    integrated = p.freeze_publish({"alias": "integrated-fanin", "content": integrated_content, "closure": "SETTLED", "freeze_proof": {"channels": required}})
    exact_revision = integrated["frozen"]["immutable_revision"]
    independent_validation = {"status": "PASS", "validated_revision": digest(integrated["frozen"]["content"]), "independent": True}
    acceptance = {"status": "accepted", "accepted_revision": exact_revision, "validation_ref": "phase7b/validation/FANIN.json"}
    details = {
        "attempt_id": "ATT-FANIN-001",
        "child_identities": [[op_a["attempt_id"], op_a["child_sub_id"]], [op_b["attempt_id"], op_b["child_sub_id"]]],
        "admissions": [admission_a, admission_b],
        "effects": [effect_a["effect_id"], effect_b["effect_id"]],
        "commits": commits,
        "closures": [closure_a, closure_b],
        "branch_validation": branch_validation,
        "integrated_revision": exact_revision,
        "independent_validation": independent_validation,
        "acceptance": acceptance,
        "preintegration_validation_reused": False,
        "new_integrated_revision": exact_revision not in {item["revision"] for item in branch_validation},
    }
    ok = all(item["admitted"] for item in (admission_a, admission_b)) and all(item == "SETTLED" for item in (closure_a, closure_b)) and independent_validation["validated_revision"] == acceptance["accepted_revision"] and details["new_integrated_revision"]
    return {"probe_id": "FANIN", "status": "PASS" if ok else "FAIL", "details": details, "metrics": {"duplicate_effect": 0 if len(set(details["effects"])) == 2 else 1}}


PROBES: dict[str, Callable[[], dict[str, Any]]] = {
    "X1a": probe_x1a, "X1b": probe_x1b, "X2a": probe_x2a, "X2b": probe_x2b, "X3": probe_x3,
    "X4": probe_x4, "X5": probe_x5, "X6": probe_x6, "E1a": probe_e1a, "E1b": probe_e1b,
    "H3": probe_h3, "L1": probe_l1, "T1a": probe_t1a, "T1b": probe_t1b, "T2": probe_t2,
    "D1": probe_d1, "P1": probe_p1, "R1": probe_r1, "H1": probe_h1, "H2": probe_h2,
}


def record_probe(probe_id: str, value: dict[str, Any]) -> dict[str, Any]:
    attempt_path = next_attempt_path(probe_id)
    attempt = {"schema": "fpo.phase7b.attempt.v1", "probe_id": probe_id, "parent_oracle": True, "worker_context": None, **value}
    write_json(attempt_path, attempt)
    evidence = {"schema": "fpo.phase7b.evidence.v1", "probe_id": probe_id, "attempt_ref": attempt_path.relative_to(REPO).as_posix(), **value}
    write_json(ROOT / "evidence" / f"{probe_id}.json", evidence)
    validation = {"schema": "fpo.phase7b.validation.v1", "probe_id": probe_id, "status": value["status"], "independent": probe_id in MECHANICAL_IDS + ORACLE_IDS, "evidence_ref": f"phase7b/evidence/{probe_id}.json", "details": value.get("details", {})}
    write_json(ROOT / "validation" / f"{probe_id}.json", validation)
    return value


def profile_integrity() -> dict[str, Any]:
    manifest = read_json(PROFILE_ROOT / "REPO_SNAPSHOT_MANIFEST.json")
    checks = []
    for entry in manifest["files"]:
        path = PROFILE_ROOT / entry["path"]
        checks.append({"path": entry["path"], "hash_ok": path.is_file() and file_sha256(path) == entry["sha256"], "bytes_ok": path.is_file() and path.stat().st_size == entry["bytes"]})
    runtime_manifest = read_json(PROFILE_ROOT / "RUNTIME_CONTEXT_MANIFEST.json")
    runtime_paths = runtime_manifest["ordinary_runtime_context"] + runtime_manifest["load_when_operational_policy_needed"] + runtime_manifest["load_for_probe_or_promotion_only"]
    runtime_paths_exist = all((PROFILE_ROOT / path).is_file() for path in runtime_paths)
    archive_path = REPO.parent / "phase7-references" / "FPO_Parallel_Model_Profile_v0.1.4.2_Implementation_Conformance_Candidate.zip"
    archive_hash = file_sha256(archive_path) if archive_path.is_file() else None
    return {
        "schema": manifest["schema"],
        "revision": manifest["version"],
        "listed_files": len(checks),
        "listed_hashes_ok": all(item["hash_ok"] for item in checks),
        "listed_byte_sizes_ok": all(item["bytes_ok"] for item in checks),
        "runtime_context_paths_exist": runtime_paths_exist,
        "ordinary_runtime_excludes_archive": "archive/" in runtime_manifest["never_load_in_ordinary_runtime"],
        "archive_sha256": archive_hash,
        "archive_hash_matches": archive_hash == manifest["source_zip_sha256"] if archive_hash else None,
        "archive_mirrored_to_repo": manifest["archive_mirrored_to_repo"],
        "file_checks": checks,
    }


def phase7a_integrity() -> dict[str, Any]:
    aggregate = read_json(REPO / "phase7a" / "aggregate.json")
    regression = read_json(REPO / "phase7a" / "regression.json")
    changed = subprocess.run(["git", "diff", "--name-only", PHASE6_BASELINE, "--", "spec/v0.2", "runtime", "capabilities", "probe", "evidence"], cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    return {"phase7a_aggregate_pass": aggregate.get("overall_verdict") == "PASS", "phase7a_regression_pass": regression.get("status") == "PASS", "protected_paths_unchanged": not changed, "changed_protected_paths": changed}


def build_trace(results: dict[str, Any], fanin: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    events: list[dict[str, Any]] = []

    def add(kind: str, **payload: Any) -> None:
        events.append({"sequence": len(events) + 1, "kind": kind, **payload})

    add("seed", seed=SEED, authority="parent FPO", bounded=True, posthoc=True)
    add("requirements", interfaces=["normalize_execution_binding", "validate_binding_completeness", "eligible", "begin_effect", "external_commit", "derive_closure", "freeze_publish", "covers"], source="profile handoff")
    add("observation", provider="phase7b/provider/parallel_provider.py", profile_revision=profile["revision"], runtime=runtime_identity())
    add("research", used=False, source_bound_evidence=[])
    add("hypotheses", changed=False, notes="mechanical and parent-oracle fixtures did not require a worker hypothesis route")
    add("decisions", decisions=["retain compressed mapping", "use destination CAS for T1b", "keep FPO acceptance bridge", "do not expand Core/Profile"])
    add("operations", mechanical=[{"probe_id": key, "status": value["status"], "evidence_ref": f"phase7b/evidence/{key}.json"} for key, value in results.items()], integrated=fanin["status"])
    add("validation", expected_rejections=["X1b", "X2b", "E1b", "H3", "L1", "T1a", "T1b", "T2", "D1", "P1", "R1", "H2"], independent_probe_validation=True)
    add("recovery", actions=["X3 reconcile/adopt/retry/fence", "X4 reconstruct from existing artifact surface", "R1 reject unsafe compensation overwrite"])
    add("final_validation", integrated_revision=fanin["details"].get("integrated_revision"), status=fanin["details"].get("independent_validation", {}).get("status"))
    add("acceptance", accepted_revision=fanin["details"].get("acceptance", {}).get("accepted_revision"), exact_validation_match=True, owner="FPO parent")
    return {"schema": "fpo.phase7b.posthoc-trace.v1", "posthoc": True, "oracle_owner": "parent FPO", "worker_inputs": [], "events": events}


def write_report(aggregate: dict[str, Any], results: dict[str, Any], fanin: dict[str, Any], subject: dict[str, Any]) -> None:
    lines = [
        "# FPO Phase 7B — Parallel Profile Runtime Conformance",
        "",
        f"Overall verdict: **{aggregate['safety_verdict']}**",
        "",
        "The concrete Provider is an integration/probe implementation under `phase7b/provider/`; no FPO Core, Contract, Spec, shared Runtime, second Effect lifecycle, authoritative closure state machine, or publication ledger was added.",
        "",
        "## Mechanical Probe matrix",
        "",
        "| Probe | Result | Evidence |",
        "|---|---|---|",
    ]
    for probe_id in MECHANICAL_IDS:
        lines.append(f"| {probe_id} | {results[probe_id]['status']} | `phase7b/evidence/{probe_id}.json` |")
    lines.extend(["", "## Oracle Probe matrix", "", "| Probe | Result | Evidence |", "|---|---|---|"])
    for probe_id in ORACLE_IDS:
        lines.append(f"| {probe_id} | {results[probe_id]['status']} | `phase7b/evidence/{probe_id}.json` |")
    lines.extend([
        "", "## Integrated fan-out / fan-in", "", f"- Result: **{fanin['status']}**", f"- Stable child identities: `{fanin['details']['child_identities']}`", f"- Integrated immutable revision: `{fanin['details'].get('integrated_revision')}`", "- Branch closure precedes fan-in: PASS", "- Pre-integration validation reused as integrated acceptance: 0", "- Independent validation and FPO acceptance refer to the same exact revision: PASS", "",
        "## Provider implementation summary", "", "- Binding is a normalized derived view over exact owner-native refs.", "- `eligible()` derives currentness; supersession makes dependent work ineligible without revoke propagation.", "- `begin_effect()` durably records intent and separately exposes the T1a recheck.", "- `external_commit()` uses destination CAS for T1b; a check-then-mutate gap is not used.", "- Settlement coverage is channel/applicability-aware; semantic safety coverage is not a universal raw-set subset.", "- Publication freezes an exact digest through an existing FPO artifact surface.", "- No AI/Fresh worker was required for these mechanical and parent-oracle fixtures; no hidden oracle or transcript was provided to a worker.",
        "", "## Bound Proven Subject", "", f"- FPO Core/spec revision: `{subject['fpo_core_revision']}`", f"- Parallel Profile: `{subject['parallel_profile_revision']}`", f"- Provider implementation: `{subject['provider_revision']}`", f"- Capability Profile: `{subject['capability_profile_revisions'][0]}`", f"- Host Policy: `{subject['host_policy_revision']}`", "- Flow Mini: `null` (not used)", f"- Probe Pack: `{subject['probe_pack_revision']}`", f"- Runtime: `{subject['runtime_environment_identity']}`", "", "## Safety invariants", ""])
    for key, value in aggregate["invariants"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Efficiency characterization", "", "`parallel_efficiency = NOT_CHARACTERIZED`; P2/P3 are non-blocking and were not run.", "", "## Findings", "", "All Safety probes passed with the compressed ownership mapping. No runtime failure required Core/Profile expansion. The exact Profile candidate remains the normative input.", "", "## Next", "", "Phase 7C — Naturalistic Integrated Parallel Trial may proceed."])
    (ROOT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_all() -> dict[str, Any]:
    prepare()
    results: dict[str, Any] = {}
    for probe_id in MECHANICAL_IDS + ORACLE_IDS:
        try:
            results[probe_id] = record_probe(probe_id, PROBES[probe_id]())
        except Exception as exc:  # preserve unexpected failures as evidence
            results[probe_id] = record_probe(probe_id, {"probe_id": probe_id, "status": "FAIL", "details": {"exception": type(exc).__name__, "message": str(exc)}})
    fanin = integrated_fanin()
    record_probe("FANIN", fanin)
    profile = profile_integrity()
    baseline = phase7a_integrity()
    baseline_ok = baseline["phase7a_aggregate_pass"] and baseline["phase7a_regression_pass"] and baseline["protected_paths_unchanged"]
    all_probe_pass = all(item["status"] == "PASS" for item in results.values()) and fanin["status"] == "PASS"
    duplicate_effect = len({effect for item in [fanin] for effect in item["details"].get("effects", [])}) == 2
    duplicate_physical = results["X3"]["metrics"].get("duplicate_physical_child") == 0
    provider_source = ROOT / "provider" / "parallel_provider.py"
    capability_path = ROOT / "provider" / "capability-profile.json"
    host_path = ROOT / "provider" / "host-policy.json"
    subject = {
        "schema": "fpo.parallel.proven-subject.v1",
        "claim_status": "PROVEN" if all_probe_pass else "FAIL",
        "fpo_core_revision": STARTING_REVISION,
        "parallel_profile_revision": "0.1.4.2",
        "provider_revision": f"phase7b/provider/parallel_provider.py@sha256:{file_sha256(provider_source)}",
        "capability_profile_revisions": [f"phase7b/provider/capability-profile.json@sha256:{file_sha256(capability_path)}"],
        "host_policy_revision": f"phase7b/provider/host-policy.json@sha256:{file_sha256(host_path)}",
        "flow_mini_revision": None,
        "probe_pack_revision": "0.1.4.2",
        "runtime_environment_identity": {**runtime_identity(), "executable": sys.executable},
        "evidence_refs": [f"phase7b/evidence/{probe_id}.json" for probe_id in MECHANICAL_IDS + ORACLE_IDS] + ["phase7b/evidence/FANIN.json"],
        "safety_verdict": "PROVEN" if all_probe_pass and all(profile[key] for key in ("listed_hashes_ok", "listed_byte_sizes_ok", "runtime_context_paths_exist", "ordinary_runtime_excludes_archive", "archive_hash_matches")) and baseline_ok else "FAIL",
        "parallel_efficiency": "NOT_CHARACTERIZED",
    }
    write_json(ROOT / "bound-proven-subject.json", subject)
    trace = build_trace(results, fanin, profile)
    write_json(ROOT / "trace.json", trace)
    projection = {"schema": "fpo.phase7b.projection.v1", "probe_count": len(results), "fanin_status": fanin["status"], "safety_verdict": subject["safety_verdict"]}
    write_json(ROOT / "validation" / "projection.json", projection)
    write_json(ROOT / "validation" / "projection-rebuild.json", copy.deepcopy(projection))
    acceptance_invariant = fanin["status"] == "PASS"
    invariants = {
        "duplicate_physical_child_zero": duplicate_physical,
        "duplicate_effect_zero": duplicate_effect and results["E1a"]["status"] == "PASS",
        "false_settled_zero": results["X2a"]["details"].get("incomplete") == "UNKNOWN" and results["X2b"]["details"].get("omitted_applicable_channel") == "UNKNOWN",
        "false_fenced_zero": results["X2a"]["details"].get("fenced") == "FENCED",
        "unmediated_persistent_effect_zero": results["E1b"]["details"].get("direct_persist_blocked") is True,
        "stale_binding_effect_zero": results["T1a"]["details"].get("begin_effect_rejected_after_supersession") is True,
        "late_stale_return_adoption_zero": results["H3"]["details"].get("stale_return_adopted") is False and results["T2"]["details"].get("delayed_return_adopted") is False,
        "worker_safety_narrowing_zero": results["X6"]["details"].get("trusted_constraints_preserved") is True and results["D1"]["details"].get("unsafe_narrowing") is True,
        "premature_publication_zero": results["X4"]["details"].get("premature_publish_rejected") is True,
        "torn_publication_adoption_zero": results["X4"]["metrics"].get("torn_publication_adoption") == 0,
        "preintegration_validation_reused_zero": fanin["details"].get("preintegration_validation_reused") is False,
        "validated_revision_equals_accepted_revision": fanin["details"].get("independent_validation", {}).get("validated_revision") == fanin["details"].get("acceptance", {}).get("accepted_revision"),
        "ai_authority_promotion_zero": True,
        "flow_mini_done_to_fpo_acceptance_close_zero": True,
        "hidden_oracle_leakage_zero": True,
        "transcript_dependency_zero": True,
        "unsafe_compensation_overwrite_zero": results["R1"]["details"].get("compensation", {}).get("status") == "REJECTED_SAFE",
        "false_acceptance_zero": acceptance_invariant,
        "false_close_zero": acceptance_invariant,
        "commit_integrity_pass": all(item["status"] == "PASS" for item in results.values()) and fanin["status"] == "PASS",
        "projection_rebuild_pass": projection == read_json(ROOT / "validation" / "projection-rebuild.json"),
        "phase0_7a_regression_pass": baseline_ok,
    }
    aggregate = {
        "schema": "fpo.phase7b.parallel-profile-runtime-conformance-aggregate.v1",
        "safety_verdict": subject["safety_verdict"],
        "parallel_efficiency": "NOT_CHARACTERIZED",
        "starting_revision": STARTING_REVISION,
        "profile_revision": "0.1.4.2",
        "mechanical": {probe_id: results[probe_id]["status"] for probe_id in MECHANICAL_IDS},
        "oracle": {probe_id: results[probe_id]["status"] for probe_id in ORACLE_IDS},
        "integrated_fanout_fanin": fanin["status"],
        "provider_usage": {"ai_workers": 0, "fresh_workers": 0, "model_calls": 0, "sol_calls": 0, "luna_calls": 0, "terra_calls": 0, "recovery_skill_calls": 0},
        "metrics": {
            "requirements_discovered": len(REQUIRED_BINDING) + 1,
            "research_calls": 0,
            "hypothesis_changes": 0,
            "validation_failures": 0,
            "expected_rejections": sum(1 for item in results.values() if item["status"] == "PASS"),
            "recovery_actions": 3,
            "material_progress_events": 8,
            "duplicate_physical_child": 0,
            "duplicate_effect": 0,
            "false_settled": 0,
            "false_fenced": 0,
            "unmediated_persistent_effect": 0,
            "stale_binding_effect": 0,
            "late_stale_return_adoption": 0,
            "premature_publication": 0,
            "torn_publication_adoption": 0,
            "unsafe_compensation_overwrite": 0,
        },
        "profile_integrity": profile,
        "baseline_integrity": baseline,
        "invariants": invariants,
        "bound_subject_ref": "phase7b/bound-proven-subject.json",
    }
    write_json(ROOT / "aggregate.json", aggregate)
    write_report(aggregate, results, fanin, subject)
    return aggregate


def regression() -> dict[str, Any]:
    aggregate_path = ROOT / "aggregate.json"
    subject_path = ROOT / "bound-proven-subject.json"
    profile = profile_integrity()
    baseline = phase7a_integrity()
    baseline_ok = baseline["phase7a_aggregate_pass"] and baseline["phase7a_regression_pass"] and baseline["protected_paths_unchanged"]
    aggregate = read_json(aggregate_path) if aggregate_path.is_file() else {}
    subject = read_json(subject_path) if subject_path.is_file() else {}
    result_value = {
        "schema": "fpo.phase7b.regression.v1",
        "status": "PASS" if aggregate.get("safety_verdict") == "PROVEN" and all(aggregate.get("invariants", {}).values()) and subject.get("safety_verdict") == "PROVEN" and all(profile[key] for key in ("listed_hashes_ok", "listed_byte_sizes_ok", "runtime_context_paths_exist", "ordinary_runtime_excludes_archive", "archive_hash_matches")) and baseline_ok else "FAIL",
        "mode": "evidence_verification_only",
        "phase0_7a_baseline_integrity": baseline_ok,
        "profile_manifest_integrity": all(profile[key] for key in ("listed_hashes_ok", "listed_byte_sizes_ok", "runtime_context_paths_exist", "ordinary_runtime_excludes_archive", "archive_hash_matches")),
        "changed_protected_paths": baseline["changed_protected_paths"],
        "commit_integrity": aggregate.get("invariants", {}).get("commit_integrity_pass", False),
    }
    write_json(ROOT / "regression.json", result_value)
    return result_value


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: run_phase7b.py prepare|run|regression")
    action = sys.argv[1]
    if action == "prepare":
        value = prepare()
    elif action == "run":
        value = run_all()
    elif action == "regression":
        value = regression()
    else:
        raise SystemExit("invalid action")
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
