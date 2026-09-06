"""Bounded Provider implementation for the v0.1.4.2 conformance probe.

This module is deliberately a probe/integration implementation.  It does not
create an FPO authority record, a second Effect lifecycle, a publication
ledger, or a scheduler.  Binding, eligibility, and closure are derived from
the inputs supplied by the owner-native state and the Provider proof surface.
"""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import sys
import threading
from dataclasses import dataclass
from typing import Any, Iterable


class ProviderError(RuntimeError):
    """Base error for a safely rejected Provider operation."""


class StaleBindingError(ProviderError):
    pass


class IncompleteBindingError(ProviderError):
    pass


class MediationError(ProviderError):
    pass


class CasConflictError(ProviderError):
    pass


class UnknownOutcomeError(ProviderError):
    pass


class CompositionConflictError(ProviderError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def runtime_identity() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


class BindingCoverage:
    """Exact component coverage for normalized Execution Binding."""

    @staticmethod
    def _components(supplied: Any) -> dict[str, dict[str, Any]]:
        if isinstance(supplied, dict):
            items = supplied.get("components", [])
        else:
            items = supplied
        return {str(item["name"]): item for item in items if isinstance(item, dict) and "name" in item}

    @classmethod
    def covers(cls, required: Any, supplied: Any) -> bool:
        components = cls._components(supplied)
        for requirement in required or []:
            name = requirement if isinstance(requirement, str) else requirement.get("name")
            if not name or name not in components:
                return False
            component = components[name]
            ref = component.get("ref")
            if not isinstance(ref, dict) or not ref.get("revision") or not ref.get("digest"):
                return False
            if isinstance(requirement, dict):
                expected = requirement.get("ref") or {}
                for key in ("revision", "digest"):
                    if key in expected and ref.get(key) != expected[key]:
                        return False
        return True


class SettlementCoverage:
    """Coverage for applicable mutation channels and terminal/fence proof."""

    TERMINAL = {"terminal", "settled", "absent", "closed"}

    @staticmethod
    def _required(required: Iterable[Any]) -> list[dict[str, Any]]:
        result = []
        for item in required or []:
            if isinstance(item, str):
                result.append({"channel": item, "applicable": True})
            else:
                result.append(dict(item))
        return [item for item in result if item.get("applicable", True)]

    @classmethod
    def covers(cls, required: Any, supplied: Any) -> bool:
        required_items = cls._required(required)
        if isinstance(supplied, dict):
            supplied_items = supplied.get("observations", supplied.get("channels", []))
            fence_proof = supplied.get("proof_kind") == "fence"
        else:
            supplied_items = supplied or []
            fence_proof = False
        proofs = {
            str(item.get("channel")): item
            for item in supplied_items
            if isinstance(item, dict) and item.get("channel")
        }
        for item in required_items:
            proof = proofs.get(str(item["channel"]))
            allowed_statuses = cls.TERMINAL | ({"fenced"} if fence_proof else set())
            if not proof or proof.get("status") not in allowed_statuses:
                return False
            if not proof.get("proof"):
                return False
        return True


class SemanticSafetyCoverage:
    """Semantic no-narrowing coverage; not a universal set-subset validator."""

    SET_FIELDS = ("dependencies", "conflict_domains", "invariants")

    @classmethod
    def covers(cls, required: Any, supplied: Any) -> bool:
        trusted = required or {}
        claim = supplied or {}
        for field in cls.SET_FIELDS:
            if not set(trusted.get(field, [])) <= set(claim.get(field, [])):
                return False
        trusted_restrictions = trusted.get("capability_restrictions", {})
        claim_restrictions = claim.get("capability_restrictions", {})
        for key, trusted_value in trusted_restrictions.items():
            if trusted_value is True and claim_restrictions.get(key) is not True:
                return False
            if isinstance(trusted_value, list) and not set(trusted_value) <= set(claim_restrictions.get(key, [])):
                return False
        # The provider path and effect class are semantic commitments, not sets.
        for field in ("effect_class", "provider_path"):
            if trusted.get(field) and claim.get(field) != trusted[field]:
                return False
        return True


def covers(required: Any, supplied_or_proven: Any, domain: str) -> bool:
    """Shared interface with deliberately domain-specific implementations."""

    if domain == "binding":
        return BindingCoverage.covers(required, supplied_or_proven)
    if domain == "settlement":
        return SettlementCoverage.covers(required, supplied_or_proven)
    if domain == "semantic_safety":
        return SemanticSafetyCoverage.covers(required, supplied_or_proven)
    raise ValueError(f"unknown coverage domain: {domain}")


@dataclass
class Destination:
    revision: str
    value: Any
    lock: threading.Lock


class ParallelProvider:
    """Small concrete provider used by the Phase 7B mechanical/oracle probes."""

    def __init__(self, capability_profile: dict[str, Any], host_policy: dict[str, Any] | None = None) -> None:
        self.capability_profile = copy.deepcopy(capability_profile)
        self.host_policy = copy.deepcopy(host_policy or {})
        self.effect_intents: dict[str, dict[str, Any]] = {}
        self.spawn_mappings: dict[tuple[str, str], dict[str, Any]] = {}
        self.physical_children: dict[str, dict[str, Any]] = {}
        self.destinations: dict[str, Destination] = {}
        self.artifact_surface: dict[str, dict[str, Any]] = {}
        self.slot_occupancy: set[str] = set()
        self.mutation_occupancy: dict[str, str] = {}
        self.events: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def _event(self, kind: str, **payload: Any) -> dict[str, Any]:
        event = {"sequence": len(self.events) + 1, "kind": kind, **payload}
        self.events.append(event)
        return event

    def register_destination(self, name: str, value: Any, revision: str = "r0") -> None:
        self.destinations[name] = Destination(revision=revision, value=copy.deepcopy(value), lock=threading.Lock())

    def normalize_execution_binding(self, operation: dict[str, Any], effect_context: dict[str, Any]) -> dict[str, Any]:
        refs = operation.get("refs", operation)
        # Required binding components are trusted Provider/Capability profile
        # input.  A worker-supplied or effect-context override is not allowed to
        # narrow this list.
        required = self.capability_profile.get("required_binding", [])
        components: list[dict[str, Any]] = []
        for requirement in required:
            name = requirement if isinstance(requirement, str) else requirement.get("name")
            ref = refs.get(name)
            if isinstance(ref, dict):
                component = {"name": name, "ref": copy.deepcopy(ref), "source": ref.get("source", "owner-native")}
            elif ref is not None:
                component = {"name": name, "ref": {"revision": str(ref), "digest": digest(ref)}, "source": "owner-native"}
            else:
                component = {"name": name, "ref": None, "source": "owner-native"}
            components.append(component)
        components.sort(key=lambda item: item["name"])
        binding = {
            "schema": "fpo.parallel.execution-binding.derived.v1",
            "components": components,
            "attempt_id": operation.get("attempt_id"),
            "child_sub_id": operation.get("child_sub_id"),
            "child_identity": [operation.get("attempt_id"), operation.get("child_sub_id")],
        }
        binding["execution_basis_fingerprint"] = digest(binding)
        return binding

    def validate_binding_completeness(self, required: Any, binding: dict[str, Any]) -> bool:
        return covers(required, binding, "binding")

    def _binding_matches_current(self, binding: dict[str, Any], current_refs: dict[str, Any]) -> bool:
        for component in binding.get("components", []):
            name = component.get("name")
            if name not in current_refs or component.get("ref") != current_refs[name]:
                return False
        return True

    def eligibility_reasons(self, operation: dict[str, Any], effect_context: dict[str, Any]) -> list[str]:
        binding = operation.get("binding") or self.normalize_execution_binding(operation, effect_context)
        required = self.capability_profile.get("required_binding", [])
        reasons: list[str] = []
        if not self.validate_binding_completeness(required, binding):
            reasons.append("binding_incomplete")
        if not self._binding_matches_current(binding, effect_context.get("current_owner_refs", {})):
            reasons.append("binding_not_current")
        if operation.get("attempt_id") != effect_context.get("current_attempt_id", operation.get("attempt_id")):
            reasons.append("attempt_not_current")
        if effect_context.get("approval_authority_valid") is not True:
            reasons.append("approval_invalid")
        if effect_context.get("material_observations_current", True) is not True:
            reasons.append("material_observation_stale")
        if effect_context.get("enforced_capability_envelope_valid", True) is not True:
            reasons.append("capability_envelope_invalid")
        if effect_context.get("parallel_composition_constraints_satisfied", True) is not True:
            reasons.append("composition_not_safe")
        return reasons

    def eligible(self, operation: dict[str, Any], effect_context: dict[str, Any]) -> bool:
        reasons = self.eligibility_reasons(operation, effect_context)
        self._event("eligibility-derived", eligible=not reasons, reasons=reasons, binding_fingerprint=(operation.get("binding") or {}).get("execution_basis_fingerprint"))
        return not reasons

    def begin_effect(self, effect_intent: dict[str, Any], current_context: dict[str, Any]) -> dict[str, Any]:
        operation = copy.deepcopy(effect_intent.get("operation", {}))
        binding = self.normalize_execution_binding(operation, current_context)
        effect_intent = copy.deepcopy(effect_intent)
        effect_intent["binding"] = binding
        if not self.eligible({**operation, "binding": binding}, current_context):
            self._event("effect-currentness-recheck", effect_id=effect_intent.get("effect_id"), accepted=False)
            raise StaleBindingError("T1a currentness recheck rejected Effect authority")
        if effect_intent.get("path") not in {"begin_effect", "mediated"} or effect_intent.get("registrable") is not True:
            raise MediationError("Effect path is not registrable/mediated")
        effect_id = effect_intent.get("effect_id") or f"effect:{operation.get('attempt_id')}:{operation.get('child_sub_id')}:{effect_intent.get('mutation_id')}"
        existing = self.effect_intents.get(effect_id)
        if existing:
            if existing["binding"]["execution_basis_fingerprint"] != binding["execution_basis_fingerprint"]:
                raise StaleBindingError("stable Effect identity was reused with a different binding")
            return copy.deepcopy(existing)
        durable = {
            "schema": "fpo.parallel.effect-intent.derived.v1",
            "effect_id": effect_id,
            "attempt_id": operation.get("attempt_id"),
            "child_identity": [operation.get("attempt_id"), operation.get("child_sub_id")],
            "binding": binding,
            "state": "OPEN",
            "mutation_domain": effect_intent.get("mutation_domain"),
            "currentness_recheck": True,
            "mediated": True,
        }
        self.effect_intents[effect_id] = durable
        self._event("effect-intent-durable", effect_id=effect_id, binding_fingerprint=binding["execution_basis_fingerprint"])
        self._event("effect-currentness-recheck", effect_id=effect_id, accepted=True)
        return copy.deepcopy(durable)

    def external_commit(self, effect_id: str, mutation: dict[str, Any], current_context: dict[str, Any] | None = None) -> dict[str, Any]:
        effect = self.effect_intents.get(effect_id)
        if not effect:
            raise ProviderError("unknown Effect identity")
        if effect["state"] == "COMMITTED":
            return copy.deepcopy(effect["commit"])
        if effect["state"] != "OPEN":
            raise ProviderError(f"Effect is not commit-ready: {effect['state']}")
        destination_name = mutation["destination"]
        destination = self.destinations[destination_name]
        expected_revision = mutation["expected_revision"]
        with destination.lock:
            if destination.revision != expected_revision:
                self._event("external-commit-cas-rejected", effect_id=effect_id, destination=destination_name)
                raise CasConflictError("destination CAS rejected concurrent/stale mutation")
            new_revision = mutation.get("new_revision") or f"{effect_id}:committed"
            destination.value = copy.deepcopy(mutation["value"])
            destination.revision = new_revision
            commit = {
                "schema": "fpo.parallel.external-commit-proof.v1",
                "effect_id": effect_id,
                "destination": destination_name,
                "expected_revision": expected_revision,
                "result_revision": new_revision,
                "mechanism": "destination-CAS",
            }
            effect["state"] = "COMMITTED"
            effect["commit"] = commit
            self._event("external-commit-cas-accepted", effect_id=effect_id, destination=destination_name, result_revision=new_revision)
            return copy.deepcopy(commit)

    def direct_persist(self, destination: str, value: Any) -> None:
        raise MediationError(f"direct persistent mutation is unavailable for {destination}")

    def required_channels(self, operation: dict[str, Any], newly_known: Iterable[dict[str, Any]] = ()) -> list[dict[str, Any]]:
        base = [dict(item) for item in operation.get("required_at_spawn", [])]
        seen = {item.get("channel") for item in base}
        for candidate in newly_known:
            applies = candidate.get("applies_to", {})
            if (
                applies.get("capability") == operation.get("capability")
                and applies.get("effect_class") == operation.get("effect_class")
                and applies.get("provider_path") == operation.get("provider_path")
            ) and candidate.get("channel") not in seen:
                base.append(dict(candidate))
                seen.add(candidate.get("channel"))
        return base

    def derive_closure(self, required_channels: Any, observations: Any, fence_proof: Any) -> str:
        if covers(required_channels, observations, "settlement"):
            return "SETTLED"
        if fence_proof and covers(required_channels, {"proof_kind": "fence", "observations": fence_proof}, "settlement"):
            return "FENCED"
        return "UNKNOWN"

    def freeze_publish(self, subject: dict[str, Any]) -> dict[str, Any]:
        closure = subject.get("closure")
        if closure not in {"SETTLED", "FENCED"}:
            raise ProviderError("publication requires SETTLED or FENCED closure")
        content = copy.deepcopy(subject.get("content"))
        content_digest = digest(content)
        alias = subject.get("alias") or f"integrated:{content_digest}"
        existing = self.artifact_surface.get(alias)
        if existing and existing["content_digest"] != content_digest:
            raise ProviderError("mutable publication alias cannot point at a new content revision")
        frozen = {
            "schema": "fpo.parallel.frozen-subject.v1",
            "immutable_revision": content_digest,
            "content": content,
            "closure": closure,
            "freeze_proof": copy.deepcopy(subject.get("freeze_proof", {"closure": closure})),
            "alias": alias,
        }
        manifest = {
            "schema": "fpo.existing.artifact-manifest.v1",
            "artifact_id": alias,
            "content_digest": content_digest,
            "immutable_revision": content_digest,
            "source": "provider-freeze",
        }
        self.artifact_surface[alias] = {"content_digest": content_digest, "frozen": frozen, "manifest": manifest}
        self._event("freeze", immutable_revision=content_digest, closure=closure)
        self._event("publish-existing-artifact-surface", artifact_id=alias, immutable_revision=content_digest)
        return {"frozen": copy.deepcopy(frozen), "artifact_manifest": copy.deepcopy(manifest)}

    def write_ahead_spawn(self, attempt_id: str, child_sub_id: str, physical_id: str) -> dict[str, Any]:
        key = (attempt_id, child_sub_id)
        existing = self.spawn_mappings.get(key)
        if existing and existing["physical_id"] != physical_id:
            raise ProviderError("stable child identity collision")
        mapping = existing or {
            "schema": "fpo.parallel.attempt-rooted-spawn-mapping.v1",
            "attempt_id": attempt_id,
            "child_sub_id": child_sub_id,
            "physical_id": physical_id,
            "status": "MAPPING_DURABLE",
            "spawn_count": 0,
        }
        self.spawn_mappings[key] = mapping
        self._event("spawn-mapping-durable", attempt_id=attempt_id, child_sub_id=child_sub_id, physical_id=physical_id)
        return copy.deepcopy(mapping)

    def spawn_child(self, attempt_id: str, child_sub_id: str, physical_state: str = "RUNNING") -> dict[str, Any]:
        key = (attempt_id, child_sub_id)
        mapping = self.spawn_mappings.get(key) or self.write_ahead_spawn(attempt_id, child_sub_id, f"physical:{attempt_id}:{child_sub_id}")
        physical_id = mapping["physical_id"]
        if physical_id not in self.physical_children:
            mapping["spawn_count"] += 1
            mapping["status"] = "SPAWNED"
            self.physical_children[physical_id] = {"physical_id": physical_id, "state": physical_state, "stable_identity": list(key)}
        return {"mapping": copy.deepcopy(mapping), "physical": copy.deepcopy(self.physical_children[physical_id])}

    def reconcile_spawn(self, attempt_id: str, child_sub_id: str, observed: str, retry_allowed: bool = True) -> dict[str, Any]:
        key = (attempt_id, child_sub_id)
        mapping = self.spawn_mappings[key]
        physical = self.physical_children.get(mapping["physical_id"])
        if observed in {"EXISTS", "RUNNING"} and physical:
            mapping["status"] = "ADOPTED"
            self._event("spawn-reconcile-adopt", stable_identity=list(key), physical_id=mapping["physical_id"])
            return {"decision": "ADOPT", "mapping": copy.deepcopy(mapping), "duplicate_physical_child": False}
        if observed == "ABSENT" and retry_allowed:
            if physical:
                raise ProviderError("ABSENT observation contradicted known physical mapping")
            result = self.spawn_child(attempt_id, child_sub_id, "RUNNING")
            self._event("spawn-reconcile-retry-stable-identity", stable_identity=list(key))
            return {"decision": "RETRY_SAME_IDENTITY", "mapping": result["mapping"], "duplicate_physical_child": False}
        if observed == "UNKNOWN":
            self._event("spawn-reconcile-unknown-fenced", stable_identity=list(key))
            return {"decision": "RECONCILE_OR_FENCE", "mapping": copy.deepcopy(mapping), "duplicate_physical_child": False}
        raise ProviderError(f"unhandled spawn observation {observed}")

    def admit_child(self, operation: dict[str, Any], effect_context: dict[str, Any], active_operations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        if not self.eligible(operation, effect_context):
            raise StaleBindingError("child admission is ineligible")
        active_operations = active_operations or []
        new_domains = set(operation.get("conflict_domains", []))
        new_invariants = set(operation.get("invariants", []))
        for active in active_operations:
            if new_domains & set(active.get("conflict_domains", [])) or new_invariants & set(active.get("invariants", [])):
                raise CompositionConflictError("semantic/physical composition conflict")
        self._event("child-admitted", child_identity=[operation.get("attempt_id"), operation.get("child_sub_id")])
        return {"admitted": True, "child_identity": [operation.get("attempt_id"), operation.get("child_sub_id")]}

    def occupy(self, child_identity: str, mutation_domain: str) -> None:
        self.slot_occupancy.add(child_identity)
        self.mutation_occupancy[mutation_domain] = child_identity

    def release_slot(self, child_identity: str) -> None:
        self.slot_occupancy.discard(child_identity)

    def can_reuse_mutation_domain(self, mutation_domain: str, closure: str) -> bool:
        return closure in {"SETTLED", "FENCED"} and mutation_domain not in self.mutation_occupancy

    def release_mutation_domain(self, mutation_domain: str, closure: str) -> bool:
        if closure not in {"SETTLED", "FENCED"}:
            return False
        self.mutation_occupancy.pop(mutation_domain, None)
        return True

    def adopt_return(self, operation: dict[str, Any], return_binding: dict[str, Any], current_context: dict[str, Any]) -> bool:
        current_binding = self.normalize_execution_binding(operation, current_context)
        accepted = current_binding["execution_basis_fingerprint"] == return_binding.get("execution_basis_fingerprint") and self.eligible({**operation, "binding": current_binding}, current_context)
        self._event("return-adoption-check", accepted=accepted)
        return accepted

    def compensate(self, effect_id: str, destination_name: str, expected_effect_revision: str, prior_value: Any, compensation_revision: str) -> dict[str, Any]:
        destination = self.destinations[destination_name]
        with destination.lock:
            if destination.revision != expected_effect_revision:
                self._event("compensation-rejected-intervening-change", effect_id=effect_id, destination=destination_name)
                return {"status": "REJECTED_SAFE", "reason": "intervening-valid-change"}
            destination.value = copy.deepcopy(prior_value)
            destination.revision = compensation_revision
            self._event("compensation-cas-accepted", effect_id=effect_id, destination=destination_name)
            return {"status": "COMPENSATED", "revision": compensation_revision}

    @staticmethod
    def planning_ready(owner_state: dict[str, Any], required_decisions: list[str]) -> bool:
        decisions = owner_state.get("decisions", {})
        return all(decisions.get(name) is not None for name in required_decisions)
