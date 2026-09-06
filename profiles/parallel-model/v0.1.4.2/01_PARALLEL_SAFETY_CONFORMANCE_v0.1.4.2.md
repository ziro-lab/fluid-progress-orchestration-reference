# 01 — Parallel Safety Conformance v0.1.4.2

Status: **NORMATIVE CANDIDATE / NOT RUNTIME PROVEN**

# A. Revision-Bound Execution

## A1. Execution Binding is a normalized view, not a new authority record

`Execution Binding` is derived from existing authoritative/owner-native state plus Provider-required exact refs.

Conceptually:

```text
ExecutionBinding =
normalize(
    FPO trusted Dispatch / Delegated Operation exact refs
  + owner-profile required refs
  + Flow Mini Core exact identity, when material
  + material observation refs, when material
  + Provider / capability binding
)
```

The binding view MUST expose its normalized component list.

An optional:

```text
execution_basis_fingerprint = hash(normalized_binding)
```

may be cached for comparison/integrity, but the opaque fingerprint alone is never authority.

Mutable aliases/projections are lookup surfaces, not sufficient authority identity.

## A2. Required binding completeness

Each capability/provider profile defines a trusted required binding specification.

Execution is ineligible if required components are missing.

Transitive omission is allowed only when a retained parent identity **mechanically commits to the omitted child's exact revision/digest**.

Allowed:

```text
Dispatch exact digest → mechanically commits to Flow Mini Core G17 digest
```

Not allowed:

```text
Plan says "use current Flow Mini"
```

## A3. Derived eligibility

No separate authoritative currentness flags are required.

```text
eligible(operation, effect) =
    binding_complete
AND binding_matches_current_owner_refs
AND operation_attempt_current
AND approval_authority_valid
AND material_observations_current
AND enforced_capability_envelope_valid
AND parallel_composition_constraints_satisfied
```

Explicit revoke remains a liveness optimization.

Correctness MUST NOT depend on revoke delivery.

When an owner-native basis becomes non-current, dependent unadopted execution products become ineligible/stale by derivation:

- running child Effect authority,
- late Return,
- staged Artifact,
- pending Effect,
- unadopted validation/evidence candidate.

## A4. Admission is not Effect authority

Admission starts work.

It does not reserve Effect authority.

### T1a
Immediately before `begin_effect`, re-evaluate the current Execution Binding/currentness predicates.

### T1b
Between successful recheck and external mutation becoming effective, one of these must hold:

1. destination CAS/fencing/conditional mutation,
2. Provider serialization of the relevant mutation domain until prior Effect settlement,
3. concurrent persistent mutation declared unsupported.

A non-atomic check-then-mutate gap is not an accepted safety mechanism.

## A5. Material observation currentness

Current actor != current world-view.

Only observations material to Effect safety/correctness require currentness/freshness treatment.

The runtime does not claim omniscient discovery of undeclared semantic dependencies; those are adversarial/oracle probe targets.

## A6. Capability envelope vs semantic safety

### Enforced capability envelope
Mechanically enforced narrowing is allowed.
Expansion requires authority.

### Semantic safety model
Worker claims may widen suspected dependency/conflict/invariant sets.
Worker claims alone may not narrow trusted constraints.

## A7. Result != Mutation Settlement

Logical child/worker success is not Mutation Closure.

`eligible=false` and physical settlement are also distinct:

- an ineligible process may still physically run,
- a running process may be safely fenced.

## A8. Mutation Closure is a derived verdict

Do not create a second authoritative lifecycle state machine for closure.

```text
closure =
  SETTLED  if all currently applicable required mutation channels are proven terminal
  FENCED   if a valid fence blocks all currently applicable required mutation channels
  UNKNOWN  otherwise
```

The proof observations/fence evidence are source material; the verdict is reconstructible.

## A9. Settlement required-set applicability

For an unresolved operation:

```text
required_channels =
required_at_spawn
UNION
newly_known_applicable_required(
    operation,
    capability,
    effect_class,
    provider_path
)
```

Do **not** union unrelated channel classes merely because they were discovered elsewhere later.

Known applicable required-channel omission mechanically invalidates `SETTLED/FENCED`.

## A10. Slot release != mutation-domain release

Compute/agent occupancy may be reclaimed while the mutation domain remains `SETTLING/UNKNOWN`.

Exclusive mutation domain reuse waits for `SETTLED/FENCED`.

---

# B. Durable Owner-State Sufficiency

## B1. No parallel authoritative Decision Ledger

A load-bearing decision is durable in the artifact/state owned by that decision.

Examples:

- FPO Definition / Plan / Policy,
- Flow Mini CONTRACT / ACCEPTANCE / WORKPLAN / Core Generation,
- Provider capability/binding profile.

## B2. Fresh actor sufficiency

A Fresh actor must be able to obtain all load-bearing execution commitments from current owner-native durable state without Planner transcript dependence.

If a material decision exists only in conversation/prose and is required for correct execution:

```text
Planning != READY
```

## B3. Owner-specific sufficiency, not universal decision schema

The Safety Profile does not impose a universal fixed handoff field list.

Each owner defines what durable content is sufficient for its responsibility.

The following guarantees remain universal:

- proposal != adoption,
- current owner-native revision is canonical,
- historical/superseded revision cannot recover authority,
- omitted material decision is a correctness failure,
- semantic completeness is tested with hidden oracle fixtures.

## B4. Coupling to Form A

Owner-state revision/currentness is consumed by `Execution Binding`.

Supersession therefore makes dependent work ineligible without a separate revoke-propagation authority mechanism.

---

# C. Safe Parallel Composition

## C1. Safety scope only

The Safety kernel retains only correctness/liveness-relevant composition constraints:

- trusted physical conflict domains,
- trusted semantic/global invariant domains,
- trusted shared assumptions where correctness-relevant,
- hard capacity/resource limits where correctness/liveness can fail,
- speculative branch eligibility/currentness,
- fan-in creates a new Integrated Revision,
- exact immutable publication and FPO validation bridge.

The following are **not** Safety Profile guarantees:

- whether to use 1/2/3 workers,
- expected marginal value,
- hedge timing,
- token/latency trade-offs,
- throughput-only shared bottlenecks,
- low-value slot preemption,
- model placement.

Those belong to Operational Policy / BENCHMARK.

## C2. Current workers can still conflict

Derived currentness does not prove compatibility.

Two current actors may be incompatible because of:

- same exclusive mutation domain,
- semantic invariant coupling,
- shared assumption failure,
- correctness-relevant hard resource capacity.

Provider admission/enforcement owns concrete composition constraints.

## C3. Fan-in creates a new subject

Merging independently produced artifacts/branches creates a new Integrated Revision.

Pre-integration validation does not automatically prove the integrated subject.

## C4. Freeze and FPO validation bridge

Provider freezes an exact immutable Integrated Revision and publishes it through existing FPO artifact/commit mechanisms.

Parallel Safety adds only this bridge invariant:

> The exact immutable revision FPO accepts MUST be the revision independently validated under existing FPO Evidence / Criteria / P4 rules.

No second Evidence or Acceptance gate is created here.
