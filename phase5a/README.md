# FPO Phase 5A — Generational Handoff / Context Continuity Probe

Phase 5A is an experiment-only area on `phase5`. It keeps the Proven Baseline
immutable and tests whether one bounded Work can continue across six Fresh AI
workers using only persisted source records, valid commits, rebuilt
projections, normative refs, workspace/evidence, and the current handoff
package.

The handoff package is a convenience projection, not a source of truth.
Versioned immutable source records and valid commits win over a missing, stale,
or contradictory handoff field. No prior worker transcript, hidden reasoning,
oracle, expected action, or previous grader result is supplied to a worker.

## Core run

```text
G1 diagnosis / minimum observation or proposal
G2 local observation / route narrowing
G3 bounded official primary-source research
G4 owner-adopted reversible repair and post-repair validation failure
G5 fresh recovery planning without resurrecting an invalidated hypothesis
G6 alternate repair, independent validation, acceptance, and close
```

The bounded fixture requires two hypothesis updates, one research operation,
route rejection, two owner-controlled repair effects, a new validation failure
after the first repair, and final independent validation. Workers never mutate
authority, execute a repair, or claim acceptance.

## Faults

- H1 removes `summary_notes`; the parent reconstructs it from immutable source.
- H2 supplies the previous-revision handoff; the current source wins and stale adoption is zero.
- H3 injects contradictory completion prose; evidence remains authoritative.
- H4 is the normal no-transcript condition; continuity is verified from source and handoff records.

## Reproduction

Use the bundled Python runtime if `python` is not on PATH:

```powershell
python phase5a/run_phase5a.py prepare-all
# start Fresh G1, then record/grade/advance; repeat through G6
python phase5a/run_phase5a.py core
python phase5a/run_phase5a.py faults
python phase5a/run_phase5a.py regression
python phase5a/run_phase5a.py report
```

The runner is a deterministic parent adapter. It does not import or modify
the normative FPO Runtime, Contract, or Spec. Context Compiler, Human-Last
re-test, multi-work scheduling, long-running wait, irreversible external
Effects, and public deployment remain out of scope.
