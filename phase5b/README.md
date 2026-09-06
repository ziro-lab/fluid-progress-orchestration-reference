# FPO Phase 5B — No-Progress / Strategy Churn / Repeated Recovery Probe

Phase 5B is an experiment-only area on `phase5`, based on the Phase 5A PASS
commit `396f63eafdbe86c4ad20f4ea86e446d527b5ecb2`. It tests whether the probe
distinguishes activity from material progress without introducing a new
normative FPO state or a single progress score.

## Cases

- N1 detects semantically duplicate strategy routes, records no material progress, and finite-stops without a hot loop.
- N2 repeats the same observation and Evidence three times; duplicate observations and duplicate Evidence gain remain non-progress.
- N3 resolves an uncertainty, eliminates a bad hypothesis, and narrows the search space while keeping the checkpoint unchanged.
- N4 applies an owner-controlled repair that worsens state, then validates an owner-authorized rollback to the known-good state as progress.
- N5 uses six Fresh generations for `FAILURE-A → recovery A → FAILURE-B → recovery B → independent validation → closed`.
- N6 exhausts useful routes / hard budget and finite-stops without Human escape.

## Result

`aggregate.json` is **PASS**. The aggregate records 11 material progress events,
0 false progress, 0 false no-progress, 1 route-churn detection, 2 duplicate
observations, 2 hypothesis eliminations, 1 rollback, 2 recoveries, 1 budget
stop, 0 hot loops, 0 false close, and 0 false acceptance.

All 12 accepted generation Returns came from Fresh child workers with no prior
transcript or hidden reasoning supplied. Initial non-conforming trial Returns
are retained under `attempts/initial/` and are not used as accepted generation
evidence.

## Invariants

False progress, false no-progress, strategy churn hot loop, invalidated route or
hypothesis resurrection, duplicate repair effect, rollback authority violation,
AI authority promotion, false close, false acceptance, and budget overrun are
all zero. Source/commit integrity, projection rebuild, acceptance after
independent validation, and Phase 5A baseline integrity are PASS.

## Reproduction

```powershell
& "$env:PYTHON" phase5b/run_phase5b.py prepare-all
& "$env:PYTHON" phase5b/run_phase5b.py core
& "$env:PYTHON" phase5b/run_phase5b.py faults
& "$env:PYTHON" phase5b/run_phase5b.py regression
& "$env:PYTHON" phase5b/run_phase5b.py report
```

Workers must be Fresh and must write only their assigned
`generations/<generation>/return.json`; the parent validates, adopts, applies
owner-controlled operations, and rebuilds projections.
