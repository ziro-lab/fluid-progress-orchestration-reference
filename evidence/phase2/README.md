# Phase 2 — Adversarial State Consistency Evidence

Overall verdict: **PASS**

The committed `phase2_matrix.json` records the Pre-Phase Gate, Gate A (D1–D4), Gate B (D5–D7), and Gate C (D8) results. Raw adversarial Return/Evidence observations are retained in each local case run during reproduction; generated run trees are intentionally excluded from Git.

| Gate | Cases | Result |
|---|---|---|
| Gate A — Return identity/freshness/binding | D1–D4 | PASS |
| Gate B — Unknown/reconciliation/partial effect | D5–D7 | PASS |
| Gate C — Conflicting evidence | D8 | PASS |

Resolved cases reached `closed / completed`. D6 and D7 stopped in explicit suspended blocker states. D8 preserved both valid conflicting Evidence records and stopped Acceptance with `UNKNOWN / unresolved`; it did not false-close.

Common invariants passed in every case: duplicate effect/adoption = 0, stale adoption = 0, wrong-bound adoption = 0, unknown-as-success = 0, false close = 0, commit integrity, projection rebuild, authority, input preservation, and finite convergence.

Reproduction entry point:

```text
python runtime/run_phase2.py preflight
python runtime/run_phase2.py matrix
```

The local Candidate under `spec/v0.2/` is authoritative for the runtime Manifest and schema.
