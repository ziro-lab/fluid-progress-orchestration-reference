# WORKPLAN

Adaptive **mutable work/resume state** for the Active Stage. It is not project history or a redefinition of correctness.

- Core Generation: P7A-I2-PLANNING-2-d32fce32

## Current Resume

- Resume Status: DONE
- Current focus: implementation and implementation-local validation completed against the current four-file Core and bounded project.
- Next safe action: none for this Stage; preserve the current implementation evidence and Return for upstream FPO review.
- Evidence subject/currentness: Execution observed the current bounded `src/badge.py` directly after the minimal change and ran the bounded suite plus focused direct-call checks.

## Remaining Work

### R1 — Align the badge implementation

- [x] Complete
- Depends on / preserves: current owner resolution, existing function signature, return shape, deterministic behavior, direct channel/version propagation, and no new unsupported-channel semantics.

Verified / observed: `src/badge.py` now maps `stable` to `green` and `canary` to `amber`, forms text from the supplied channel and version, and preserves the existing function boundary and dictionary shape.

### R2 — Establish current Stage evidence

- [x] Complete
- Depends on / preserves: Acceptance subjects, direct runtime/unit boundary, both settled channel variants, representative version propagation, and complete bounded-suite regression coverage.

Verified / observed: the bounded `unittest` suite passed 2/2; focused direct calls passed stable/canary expected values, repeated-call determinism, version propagation for `2026.08.29+build.7`, and exact `text`/`color` shape; `py_compile` passed.

### R3 — Re-ground and report the terminal Stage state

- [x] Complete
- Depends on / preserves: current canonical Core, current implementation reality, all proof obligations, minimality, and reconciliation of any blocker or partial effect.

Verified / observed: Core Generation and Controller Revision remain coherent; no Material blocker, partial effect, or reopen trigger was observed. The Stage reaches its Normal Return Point for this bounded Horizon.

## Material Warnings / Carry-forward Facts

- The old release/blue implementation conflicts with the now-authoritative owner resolution; do not treat existing behavior as an accepted baseline.
- Unsupported-channel and unusual-input behavior remains unsettled; avoid inventing it and route upward if it becomes Material.

## References

- Normative bounded project brief → `README.md` — reopen if interface, determinism, or no-invention meaning appears inconsistent with Current Reality.
- Normative owner resolution → `design/owner-resolution.md` — reopen if design currentness or settled mapping is questioned.
- Parent currentness evidence → `phase7a/evidence/I2-design-resolution.json` — reopen if the owner resolution is superseded or withdrawn.
- Fact / Evidence implementation target → `src/badge.py` at Execution start — reconcile before editing and after interruption.
- Fact / Evidence tests → `tests/test_badge.py` at Execution start — reconcile before relying on coverage.

## Final Evidence

- Current Stage is DONE for the Implementation Capability: stable/canary behavior is implemented and all current Acceptance checks have current local evidence.
- Unsupported channels and unusual input types remain outside the settled design and were not given additional semantics.
