# Phase 2 — Adversarial State Consistency

Branch: `phase2`

Phase 1 established crash durability for four deterministic cut points. Phase 2 shifts from process death to ambiguous, stale, duplicated, misbound, and conflicting external state.

## Target cases

1. **D1 — Duplicate Return**  
   The same immutable Return arrives more than once. Adoption must remain exactly once.

2. **D2 — Out-of-order Return**  
   An older Return arrives after a newer current operation/result.

3. **D3 — Stale revision Return**  
   Return references an older Dispatch / Design / state revision and must not mutate current achievement.

4. **D4 — Wrong Operation binding**  
   A valid-looking Return is bound to the wrong logical operation.

5. **D5 — Effect unknown / response loss**  
   The external effect may have happened, but response/Return is lost. Do not infer success and do not blindly retry.

6. **D6 — Provider state unknown**  
   Provider query itself cannot prove whether the operation succeeded or failed.

7. **D7 — Partial Effect**  
   Only part of the planned external effect is present. Reconcile before retry; compensate or forward-recover only through the owning policy.

8. **D8 — Conflicting Evidence**  
   Evidence for the same criterion conflicts. Acceptance must not proceed until the conflict is resolved or explicitly handled.

## Required invariants

- duplicate Effect = 0
- duplicate adoption = 0
- stale/wrong-bound Return never advances checkpoint
- unknown outcome is never promoted to success
- false close = 0
- immutable source + valid Commit determine replay state
- current projection remains rebuildable
- Runtime mechanism does not assume P3/P4/P5/P6 Authority
- all injected cases converge to an explicit finite state or a justified unresolved blocker

## Scope guard

Do not add AI Agent, Web research, multi-work scheduling, public deployment, or irreversible external effects in this phase. Core changes are not default; only failures that demonstrate a contract deficiency justify promotion changes.
