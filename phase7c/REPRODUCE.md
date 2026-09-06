# Phase 7C Reproduction Binding

Status: **CURRENT REPRODUCTION ENTRY / HISTORICAL EVIDENCE UNCHANGED**

Phase 7C's recorded PASS evidence was produced with a fixed Flow Mini r3 archive outside this repository checkout. The historical runner and evidence are retained as-is.

For a new reproduction attempt, do not rely on an implicit local layout or a guessed Flow Mini revision.

## Required Flow Mini archive

Exact file name:

`Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3.zip`

Expected SHA-256:

`454f835efac1f09d774ccc3a4bce76352761f208a6dffba9305b646f2d18f93c`

Required location relative to the FPO repository root:

`../phase7-references/Flow_Mini_Harness_v0.5.0_Implementation_Core_Convergence_Candidate_r3.zip`

This external placement is a historical Phase 7 reproduction dependency. The existence of an equivalent vendored r3 surface elsewhere in the repository does not authorize silently substituting it for this recorded archive identity.

## Current entry

Use:

```text
python phase7c/run_verified.py prepare
python phase7c/run_verified.py run
python phase7c/run_verified.py regression
```

`run_verified.py` performs archive existence and SHA-256 preflight before `run` / direct `worker` actions that actually consume the archive, then delegates to the historical `run_phase7c.py` runner. `prepare`, `report`, and evidence-only `regression` do not require the archive merely to read or prepare existing state. Missing or mismatched input fails before an archive-dependent trial starts.

Do not call a missing dependency "Flow Mini unavailable". It means only that the exact historical reproduction dependency has not been placed at the bound location.

## Proof scope

See `phase7c/PROOF_SCOPE.md` before interpreting a PASS. Phase 7C proves its deterministic local adapter / Provider integration scope; it is not a blanket proof of the current Flow Mini Plugin or live Codex Same-Sol runtime.
