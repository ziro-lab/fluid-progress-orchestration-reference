# Phase 3 Proven Evidence

Phase 3 is proven for the deterministic local sandbox probe only.

## Matrix

- `phase3_matrix.json` — Pre-Phase Gate, Gate A E1–E5, Gate B E6–E8, Gate C E9–E12, invariants, and final Phase 0–2 regression.
- `../phase1/phase1_matrix.json` — selected Phase 1 C1–C4 evidence rechecked by the Phase 3 preflight.
- `../phase2/phase2_matrix.json` — selected Phase 2 D1–D8 evidence rechecked by the Phase 3 preflight.
- `../phase0/result.json` — selected Phase 0 evidence anchor.

## Reproduction

From the repository root:

```powershell
python runtime/run_phase3.py preflight
python runtime/run_phase3.py matrix
```

The harness creates fresh case journals under `runs/phase3/`; generated run
trees remain ignored. Each case records immutable events, semantic commit
digests, a rebuildable projection, and the required control/budget/trust
metrics.

## Scope

No FPO Core, Contract, Spec, Manifest meaning, external network, credential,
real AI agent, or irreversible external Effect is included in this baseline.
