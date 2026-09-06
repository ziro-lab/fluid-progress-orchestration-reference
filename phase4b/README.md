# FPO Phase 4B — Real Research / Evidence Acquisition / Recovery Reasoning

This is an experiment-only Phase 4B area on `phase4`. It does not modify the
normative FPO Core, Contract, Spec, or shared Runtime. Core evaluation uses
bare Fresh AI workers plus public read-only Web research; no Research Skill or
Context Compiler is used.

The research Return contract separates source claims, source-bound evidence,
findings, uncertainty, proposals, and hypothesis revision. It intentionally
contains no checkpoint, acceptance, closure, Work Control, budget override, or
other FPO authority field. A Research Return can be adopted as material only.

## Core runs

```text
B1: 2 Fresh targeted-research runs
B2: 2 Fresh hypothesis-revision runs
B3: 1 Fresh version/scope conflict run
B4: 1 deterministic failed-route/alternate-route run
B5: 1 Fresh research + separate safe repair E2E run
B6: 1 Fresh bounded-unresolved run
```

The research budget is at most 3 rounds, 6 distinct queries, and 6 accepted
sources per run. Worker prompts exclude the target oracle, expected URL list,
prior output, aggregate, and report. Parent-side source artifacts are created
only after the worker Return and read-only source verification.

Reproduction uses the bundled Python runtime if `python` is not on PATH:

```powershell
python phase4b/run_phase4b.py prepare-all
# start each prepared B1/B2/B3/B5/B6 worker fresh; write only its return.json
python phase4b/run_phase4b.py grade-real
python phase4b/run_phase4b.py b4
python phase4b/run_phase4b.py b5-e2e
python phase4b/run_phase4b.py regression
python phase4b/run_phase4b.py report
```

B5 uses a Research Operation and a separate `DISP-B5-REPAIR-001` /
`OP-B5-REPAIR-001`; its repair is sandbox-local and independently validated.
Repair success text is not acceptance evidence. B6 ends in an explicit probe
blocker / `HUMAN_CANDIDATE` marker without adding a normative FPO state.
