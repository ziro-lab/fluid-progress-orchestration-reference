# FPO Phase 4A — AI Capability Boundary Probe

This directory contains experiment-only material for Phase 4A on the `phase4`
branch. It is deliberately outside `spec/v0.2/`, the normative Runtime, and
the existing Phase 0–3 evidence.

The probe measures whether a real AI capability can return bounded facts,
findings, evidence references, uncertainty, proposals, and requested
observations without gaining FPO authority. A capability Return is preserved
as untrusted data. Only the probe adapter's deterministic owner policy may
record a capability failure or adoption decision; AI text never writes
checkpoint, acceptance, closure, Work Control, budget, blocker authority, or
projection state.

## Reproduction

Prepare a fresh run directory before dispatching a fresh worker:

```powershell
python phase4a/run_phase4a.py prepare --case A1 --run-number 1
python phase4a/run_phase4a.py prepare --case A2 --run-number 1
```

Each fresh worker must read only its prepared `dispatch.json`, the named
fixture, and `contracts/ai_capability_return.schema.json`, then write only the
prepared `return.json`. It must not read an oracle, aggregate, report, or
prior result.

After the four real worker Returns are present, grade and run the injections:

```powershell
python phase4a/run_phase4a.py grade-real
python phase4a/run_phase4a.py injections
python phase4a/run_phase4a.py report
```

The final report records the Fresh worker identifiers supplied by the
orchestrator, schema and binding validation, oracle conformance, authority
promotion, false close/acceptance, immutable Return preservation, projection
rebuild, and baseline integrity.

The A1/A2 oracle files are separate from fixtures and are not input to the
worker. A3 uses valid schema data containing authority language as content.
A4 uses truncated, incomplete, and authority-field-invalid Returns; none may
be guessed into an adopted result.
