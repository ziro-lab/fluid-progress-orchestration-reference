# FPO Phase 4C — Human-Last Escalation / Irreducible Decision Boundary

Phase 4C is an experiment-only area on `phase4`. It does not modify the
normative FPO Core, Contract, Spec, or shared Runtime. The Core probe uses
bare Fresh AI workers and FPO policy; no Human-Last Skill, Research Skill, or
Context Compiler is used.

## Core runs

```text
C1: 2 Fresh — safe local autonomous route
C2: 1 Fresh — bounded public research resolves the question
C3: 1 Fresh — irreducible preference
C4: 1 Fresh — authority / approval boundary
C5: 1 Fresh — non-substitutable human observation
C6: 1 Fresh — genuine capability gap
C7: 1 Fresh — alternate route after first failure
```

There are exactly 8 required real-AI runs. C8 request-quality grading and
C9/C10 Human Response/revision tests are deterministic. Human Responses are
simulated immutable source fixtures; no real user question is sent.

## Boundary records

An AI Return may propose `NO_HUMAN` or a narrow `ESCALATE` proposal. It cannot
change FPO authority. C3–C6 use reason codes `HUMAN_PREFERENCE`,
`HUMAN_AUTHORITY`, `HUMAN_EVIDENCE`, and `HUMAN_CAPABILITY`. C1/C2/C7 must not
escalate when an autonomous route exists.

C9 binds a simulated response to the exact escalation and work revision,
validates it, then records owner adoption. C10 preserves an old response but
rejects it after the work revision changes.

## Reproduction

Use the bundled Python runtime if `python` is not on PATH:

```powershell
python phase4c/run_phase4c.py prepare-all
# start each prepared C1-C7 worker fresh; write only its return.json
python phase4c/run_phase4c.py grade-real
python phase4c/run_phase4c.py c8
python phase4c/run_phase4c.py c9
python phase4c/run_phase4c.py c10
python phase4c/run_phase4c.py regression
python phase4c/run_phase4c.py report
```

The final report and aggregate are written only after the C8–C10 deterministic
checks and regression verification complete.
