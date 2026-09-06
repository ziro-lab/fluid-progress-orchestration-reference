# 02 — Provider Implementation Conformance v0.1.4.2

Status: **NORMATIVE PROVIDER CANDIDATE / NOT FPO CORE**

Provider responsibilities are compressed to four families.

# 1. BIND / SPAWN

## 1.1 Construct normalized Execution Binding

Provider constructs the binding from:

- FPO operation/attempt-rooted trusted exact refs,
- capability-specific required owner refs,
- Flow Mini Core identity when material,
- Provider/capability binding,
- material observations when required.

The worker cannot remove required components.

Use component-level normalized representation; fingerprint is optional cache only.

## 1.2 Stable child identity

If one physical child maps 1:1 to one FPO attempt, `attempt_id` may be the idempotency root.

If one attempt can spawn multiple children:

```text
child_identity = (attempt_id, child_sub_id)
```

Avoid a redundant global ID family.

## 1.3 Write-ahead mapping

Before child spawn, durably record the attempt-rooted Provider physical mapping sufficient to reconcile the spawn.

Do not require a separate global child ledger if the mapping can live in existing Provider operation state.

## 1.4 Crash reconciliation

After restart:

- EXISTS/RUNNING → adopt/reconcile,
- ABSENT → spawn/retry same stable identity if policy allows,
- UNKNOWN → do not blind-respawn; reconcile/fence.

---

# 2. MEDIATE / BEGIN_EFFECT

All persistent/shared mutation must be reachable only through a registrable/mediated surface or an equivalent destination operation identity.

A child must not receive an unfenced direct path that can create invisible persistent/shared Effect.

## 2.1 `begin_effect` unified path

`begin_effect` performs two distinct guarantees in one Provider path:

1. durable Effect intent / equivalent destination operation identity establishment,
2. T1a currentness recheck.

These guarantees remain separately observable for Probe/Evidence even though mechanics are unified.

## 2.2 Effect intent source

Prefer mapping into the existing FPO Effect lifecycle.

Equivalent destination operation identity is allowed when it is durable, idempotent/reconcilable, and can be bound back to the FPO operation/attempt.

## 2.3 T1b external commit

After `begin_effect`:

- CAS/fence/conditional destination, or
- Provider-serialized mutation domain, or
- concurrent persistent mutation unsupported.

Response loss/unknown outcome routes to existing FPO unknown/reconcile behavior; no blind retry.

---

# 3. SETTLE

Mutation Closure is a derived verdict from observations/proofs.

## 3.1 Required mutation-channel specification

Trusted Provider/Capability profile defines required channel classes and applicability.

Examples:

- process tree,
- detached process,
- remote operation,
- CI/build job,
- provider async job,
- queued callback/write,
- fence/lease state.

## 3.2 Common no-narrowing principle

The generic rule is monotone:

> trusted required safety knowledge cannot be narrowed by untrusted/partial reporting.

But validators remain domain-specific.

### Basis coverage
Required exact binding components must be present.

### Settlement coverage
Required applicable mutation channels must be proven terminal/fenced.

### Semantic safety coverage
Trusted semantic constraints must not be weakened; this is not necessarily simple set inclusion.

Do not implement one naive universal subset validator for all domains.

## 3.3 Closure derivation

```text
SETTLED
  iff every currently applicable required channel has terminal proof

FENCED
  iff valid fence proof covers every currently applicable required mutation channel

UNKNOWN
  otherwise
```

A cached closure value is non-authoritative and must be reconstructible from proof.

## 3.4 Safety knowledge updates

For unresolved operations, newly discovered mutation-channel classes apply retroactively only when materially applicable to that operation/capability/effect/provider path.

This prevents both:

- false SETTLED from outdated safety knowledge,
- unrelated new channel discoveries from permanently poisoning old operations.

---

# 4. FREEZE / PUBLISH

## 4.1 Freeze ordering

```text
writes complete
→ closure SETTLED/FENCED
→ freeze exact immutable subject
→ durably publish through existing FPO artifact/semantic commit surface
→ expose to validator/adoption
```

## 4.2 No separate publication ledger

Do not create a second authoritative Provider publication ledger if existing FPO `artifact_manifest` / semantic commit can hold the adopted publication identity.

Provider retains only the physical freeze proof/mechanics needed to justify publication.

## 4.3 Parallel fan-in identity strengthening

For Parallel fan-in capability, Provider Profile MUST require:

- digest/content-addressed identity, or
- an equivalently immutable exact content revision identity.

A mutable alias/path alone is insufficient even if the general FPO schema permits weaker representation.

## 4.4 Validate exactly what is accepted

Validator receives the frozen exact revision.

Existing FPO Evidence/P4 owns validation/adoption semantics.

Any material change after validation creates a new revision.
