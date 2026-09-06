# Flow Mini v0.5.0 — Architecture

## Decision

v0.5 restructures only the **Implementation Planning + Execution** responsibility. Upstream Design is no longer bundled as a Core subsystem.

```text
Implementation Source
       ↓
Implementation Planning
       ↓
CONTRACT + ACCEPTANCE + WORKPLAN + EXECUTION
       ↓ Fresh context
Reconciliation Controller
       ↓
Evidence / Resume / Replan / Close
```

Optional Bare Bootstrap exists only for standalone usability.

## Why four files

The implementation layer has three semantic surfaces:

| Surface | Physical file | Lifecycle |
|---|---|---|
| Stage Truth | CONTRACT + ACCEPTANCE | Planning/REPLAN |
| Mutable Work State | WORKPLAN | Execution |
| Controller Law | EXECUTION | Harness release |

CONTRACT and ACCEPTANCE stay physically separate for lazy loading and clear `meaning vs proof obligation` ownership. POLICY merges into EXECUTION because both were fixed, always co-loaded for Execution, and had the same authority/lifecycle.

## Context simplification

v0.4.x's P0/P1/P2/P3 projection terminology is removed from the runtime model. Required behavior becomes:

**Core-first / References-lazy / Fold completed detail / Preserve Material residual / Reopen by identity.**

This keeps Fresh-context safety without a separate working-context framework.

## Planning IR integrity

PlanningはImplementation Sourceを4-Core IRへcompileする。Fresh Executorへ渡すIRは:

- **typed** — Normative / Fact-Evidence / Reference-Suggestion / Openを混同しない
- **complete** — non-local Implementation CommitmentsをCONTRACTへdurably残す
- **coherent** — CONTRACT / ACCEPTANCE / WORKPLANが同じCore Generationで揃い、Material cross-Core contradictionがない
- **controller-bound** — CONTRACTがCurrent project-local EXECUTIONの`Controller Revision`へbindされる

この保証のために新DB/lock/transaction serviceは追加しない。Generation/controller mismatchまたはMaterial cross-Core contradictionはExecution effect前にPlanningへ戻す。

## Reconciliation model

```text
Stage Truth (desired)
     +
Work State + Current Reality (current)
     ↓
Execution Controller
     ↓
reconcile → smallest safe action → observe → record
```

WORKPLAN is not a script. It is mutable resume state.

## Adaptation ownership

Planning owns Stage/architecture/dependency/Material safety-recovery-confirmation ordering/proof obligation. Execution owns local mechanics.

`verification obligation != verification mechanics`.

Equivalent or stronger exact mechanics may adapt at runtime. Changing the proof subject/boundary/strength is REPLAN.

## Preserved invariants

- Implementation Planning and Execution remain separate contexts.
- Goal Horizon != Active Stage.
- Design meaning != Planning proof obligation != Execution evidence.
- Current Reality can falsify assumptions but does not rewrite upstream meaning.
- terminal status is not proof; close re-grounds canonical state/current reality.
- stale Evidence is not Current.
- partial/unknown effects reconcile before retry.
- same unchanged failure does not bounce/retry indefinitely.
- Flow Mini does not own scheduler/locks/multi-agent conflict handling.

## Non-goals

- full Design framework
- mandatory Handoff format
- memory DB/vector retrieval
- agent orchestration/scheduling
- parallel write-set management
- hidden chain-of-thought persistence
- project-wide task tracker
