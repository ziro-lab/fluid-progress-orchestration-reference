# Phase 3 Probe Acceptance

Phase 3 is a deterministic, local-only probe. It adds no FPO Core, Contract,
Spec, Manifest, or external provider behavior.

## Gates

- Gate A — Control Authority: E1–E5
- Gate B — Resource Budget: E6–E8
- Gate C — Trust Boundary: E9–E12

Each case starts a fresh append-only journal under `runs/phase3/<case>/`.
Every journal has immutable event files, CAS-style semantic commits, content
digests, and a projection that is rebuilt from the journal source.

## Required common invariants

Every case must report PASS for:

```text
false_close
authority
unauthorized_effect
budget_overrun
dispatch_while_prohibited
duplicate_effect
duplicate_adoption
untrusted_control_promotion
commit_integrity
projection_rebuild
input_corruption
finite_convergence
```

Rejected dispatches, rejected effects, and rejected budget attempts are
recorded separately from successful invocation/effect/overrun counters. A
rejection is not itself an unauthorized effect or a budget overrun.

## Commands

```powershell
python runtime/run_phase3.py preflight
python runtime/run_phase3.py case --case E1
python runtime/run_phase3.py matrix
```

`matrix` runs Pre-Phase first and stops before the next Gate if a prior Gate
does not PASS.
