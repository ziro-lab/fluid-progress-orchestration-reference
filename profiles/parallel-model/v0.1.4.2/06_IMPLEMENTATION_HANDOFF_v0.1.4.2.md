# 06 — Implementation Handoff v0.1.4.2

Status: **STAGE-1 IMPLEMENTATION INPUT**

## Mission

Implement this Parallel/Model Profile without creating duplicate authoritative state.

## Non-negotiable "do not create"

Do NOT create unless a runtime failure proves necessity:

- standalone authoritative Execution Basis record,
- authoritative `eligible` state machine,
- authoritative Mutation Closure state machine,
- separate Provider publication ledger,
- second Effect lifecycle,
- second Evidence/Acceptance lifecycle,
- global scheduler,
- authoritative Decision Ledger,
- mandatory 3-worker role topology.

## Required implementation interfaces / predicates

### `normalize_execution_binding(...)`
Produces component-level normalized binding view from exact owner-native refs.

### `validate_binding_completeness(required, binding)`
Domain-specific exact binding completeness.

### `eligible(operation, effect_context)`
Derived predicate only.

### `begin_effect(effect_intent, current_context)`
Must:
- durably establish Effect intent/equivalent operation identity,
- perform T1a currentness check,
- enforce registrable capability mediation.

### `external_commit(...)`
Must enforce one:
- CAS/fence,
- Provider serialization,
- unsupported concurrency.

### `derive_closure(required_channels, observations, fence_proof)`
Returns:
- SETTLED,
- FENCED,
- UNKNOWN.

### `freeze_publish(subject)`
Only after closure permits publication.
Publishes exact immutable revision through existing FPO artifact/commit surface.

## Common monotone no-narrowing principle

Implement a shared interface/convention, not one naive universal set validator.

```text
covers(required, supplied_or_proven, domain) -> bool
```

Domain implementations:
- Binding coverage,
- Settlement coverage,
- Semantic safety coverage.

## Safety knowledge update rule

For unresolved operations:

```text
effective_required =
required_at_spawn
∪ newly_known_applicable_required(operation)
```

Applicability must be operation/capability/effect/provider-path specific.

## Child identity

Prefer:

```text
attempt_id
```

as root.

For multiple children:

```text
(attempt_id, child_sub_id)
```

## Runtime proof subject

Before a PROVEN claim, freeze exact:

- FPO Core/spec revision,
- Parallel Profile revision,
- Provider revision,
- Capability Profile revision(s),
- Host Policy revision,
- Flow Mini revision if used,
- Probe Pack revision,
- runtime/environment identity.
