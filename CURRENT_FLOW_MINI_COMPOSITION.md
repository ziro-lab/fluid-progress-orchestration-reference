# Current FPO × Flow Mini Plugin Composition

Status: **CURRENT OPERATIONAL BINDING / NOT CORE / NOT SPEC**

This document fixes the intended current operational composition between FPO and the Flow Mini Codex Plugin without merging their authority or lifecycle semantics.

It does not replace FPO Core, Flow Mini Core, the Parallel Profile, or Host / Provider contracts.

## 1. Current identities

FPO side:

- FPO Core / Runtime: current Proven Baseline under `spec/v0.2/` and its runtime manifest.
- FPO Parallel / Provider mapping: `profiles/parallel-model/v0.1.4.2/`.
- Current Flow Mini Capability Registry entry: `capabilities/flow_mini/CAPABILITY.json`.
- Current exact Flow Mini deployment binding: `capabilities/flow_mini/BINDING.json`.

Flow Mini side:

- Repository: `ziro-lab/Flow-Mini-Harness`.
- Exact bound commit: `462055e88346d7531c9494e011d2c1d19128f20a`.
- Plugin / Bundle version: `0.1.1`.
- Flow Mini implementation core: `v0.5.0 Implementation Core Convergence Candidate r3`.
- Controller Revision: `FM-EXEC-0.5.0-r3`.
- Standard Plugin launcher: `skills/flow-mini/SKILL.md`.
- Explicit Same-Sol Parallel launcher: `skills/flow-mini-parallel/SKILL.md`.
- Same-Sol Parallel Profile: `v0.1.2.1` when explicitly selected.

Model selection is operational policy only. A model change does not change Authority.

## 1A. Machine-selectable capability binding

`CURRENT_FLOW_MINI_COMPOSITION.md` is an operational explanation, not Runtime Control Context. It must not be smuggled into the FPO Runtime Manifest merely to make this composition available.

The actual machine-facing selection is external to Core:

```text
Capability Registry
  -> capabilities/flow_mini/CAPABILITY.json
  -> binding_ref = capabilities/flow_mini/BINDING.json
  -> exact Flow Mini Plugin commit / Bundle / Core / Controller / mode binding
  -> immutable Dispatch Packet
```

When P3 selects Flow Mini, it must resolve `capability_id = codex.flow-mini`, revision `1`, and the exact `binding_ref` before dispatch. The Dispatch must freeze the current `attempt_id`, `capability_id`, `capability_revision`, `binding_ref`, `definition_ref`, `plan_ref`, `target_revision_ref`, and `policy_revision` required by the FPO capability boundary.

A missing, stale, ambiguous, or Host-incompatible binding means **do not dispatch**. It does not mean the dependency is globally unavailable, and it does not authorize guessing a nearby Flow Mini revision.

The checked-in binding makes repository-level composition deterministic; actual Host availability/Fresh-context attestation remains a runtime observation and is not promoted by the binding file itself.

## 2. FPO-managed Standard Flow Mini

Use this route when FPO has already accepted ownership of the outer Work and delegates a bounded implementation capability to Standard Flow Mini.

```text
FPO Definition / Design / Work-level Plan
  -> delegated operation / exact attempt
  -> Flow Mini Implementation Planning
  -> PLANNING READY
  -> bound Fresh/fresh-equivalent Execution invocation
  -> Flow Mini Execution
  -> bounded implementation Return
  -> FPO P3 Return adoption
  -> FPO P4 independent Evidence / Acceptance
  -> FPO P6 Settlement / Close
```

The Flow Mini standalone launcher normally asks the user to open a Fresh task after `PLANNING READY`. Under an explicit FPO-managed delegated operation, that manual step is replaced only when the FPO / Host binding supplies a concrete Fresh/fresh-equivalent execution invocation for the same Target and Current Flow Mini Core.

Required binding before that exception is used:

- exact delegated `attempt_id` / operation identity;
- exact Target / subject identity;
- Current Flow Mini Core Generation and Controller Revision;
- Fresh/fresh-equivalent execution-context attestation;
- exact Return target back to the FPO caller;
- applicable Host / Provider capability binding.

If those are not available, do not guess. Preserve Flow Mini's ordinary Fresh-context boundary.

Flow Mini `DONE` is a capability Return. It is not FPO adoption, Acceptance, or Close.

## 3. FPO-managed Same-Sol Parallel Flow Mini

This route is **explicit only**. FPO does not automatically turn Standard Flow Mini into Parallel mode merely because parallel work appears useful.

Once explicitly selected:

- FPO retains work-level Definition / Plan / Work Control / Authority / delegated attempt / Return adoption / Acceptance / Recovery / Close.
- Flow Mini Same-Sol Supervisor owns implementation-stage planning/replan, lane admission, dispatch, local fan-in, `ADOPT/DRAIN/HOLD/CUT`, WORKPLAN mutation, and local terminal judgment.
- Provider / Host owns physical worker identity, isolation, effect mediation, stop/release, slot occupancy, and settlement proof.

FPO must not become a second lane scheduler inside the Flow Mini Stage. Flow Mini local `ADOPT`, `STAGE_ACCEPTED`, or `DONE` must not be promoted into FPO adoption, Acceptance, or Close.

Normal completion returns a bounded implementation result tied to the exact delegated attempt, exact capability binding, and current subject/revision. Materially complex recovery returns a bounded escalation packet to FPO rather than growing a second recovery system inside Flow Mini.

## 4. Recovery boundary

Keep these separate:

- transient safe failure -> bounded local retry;
- implementation-basis change -> Flow Mini REPLAN;
- Goal / Scope / design-level Acceptance meaning change -> upstream Definition / Design owner;
- repeated failure, unknown Effect, authority/currentness ambiguity, or materially complex recovery -> FPO P5 diagnosis and route adoption.

P5 chooses the recovery route but does not take product implementation, Acceptance, or Close authority.

## 5. Return / currentness boundary

A Flow Mini Return is candidate material until P3 reconciles it with the Current delegated operation.

The FPO `capability_return` message carries the Return-side identity needed to locate the exact current operation. At minimum P3 must match the Return's:

- `dispatch_id`;
- `attempt_id`;
- `provider_identity`;
- `capability_id`;
- `capability_revision`.

P3 then resolves the Current Dispatch / Delegated Operation and reconciles the operation-owned binding dimensions, including:

- `binding_ref`;
- `definition_ref`;
- `plan_ref`;
- `target_revision_ref`;
- `policy_revision`.

Do not require `binding_ref` or `target_revision_ref` to be invented as extra Return fields when the FPO Return schema does not own them there. Their authority comes from the trusted current Dispatch / Delegated Operation reached through the Return identity.

A successful worker or Flow Mini `DONE` from a superseded dispatch, attempt, capability revision, binding, Core Generation, or target remains stale/candidate-only until the owning FPO stage explicitly re-evaluates it.

## 6. Evidence boundary

Existing Phase 7 evidence has different proof scopes:

- **Phase 7A**: real-AI fixed Flow Mini r3 planning/execution capability integration for its recorded fixtures.
- **Phase 7B**: the recorded Parallel Provider / Profile conformance scope.
- **Phase 7C**: deterministic local adapter fan-out/fan-in, provider mechanics, parent-side validation/adoption separation, and operational restraint for its recorded fixtures.

Phase 7C does **not** by itself prove:

- Current Flow Mini r3 Core Activation semantics in every lane;
- REPLAN Core-Generation stale-result rejection;
- the current Codex Plugin launcher path;
- live Same-Sol Codex Host worker identity / isolation / stop / release behavior;
- every current FPO -> Flow Mini Plugin composition.

The new checked-in `CAPABILITY.json` / `BINDING.json` closes the repository-level selection ambiguity; it does **not** convert historical Phase 7C evidence into live Current Plugin proof. That requires the Current S7/S8 field observation.

## 7. Lean path

Do not route every Work through FPO merely because FPO exists.

- simple implementation work may use Flow Mini alone;
- bounded parallel work may use Flow Mini Same-Sol Parallel alone when its local boundaries are sufficient;
- add FPO when work-level Authority, Currentness, cross-stage Recovery, unknown Effects, Return adoption, independent Acceptance, or Settlement materially require it.

Once FPO has accepted ownership of a Work, do not remove its Acceptance / Settlement guarantees merely to make the run lighter.
