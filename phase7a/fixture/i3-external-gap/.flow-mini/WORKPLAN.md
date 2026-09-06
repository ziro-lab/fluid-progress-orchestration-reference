# WORKPLAN

Adaptive **mutable work/resume state** for the Active Stage. It is not project history, Product Design, or the definition of correctness.

- Core Generation: P7A-I3-PLANNING-1-G1

## Current Resume

- Resume Status: DONE
- Current focus: implementation and local validation of the Evidence-bound schema-v2 manifest builder are complete.
- Next safe action: FPO reviews this implementation Return under its own acceptance and close responsibilities.
- Blocking / wait condition: none for the authorized local implementation stage; FPO acceptance and close remain outside Flow Mini ownership.
- Pending reason + safe resume/recheck condition: none. Reopen only if the persisted Evidence or bounded project contract materially changes.
- Possible partial effect / unknown outcome: none; all local effects were observed by the focused tests and callable validation.
- Evidence subject/currentness: `phase7a/evidence/I3-research.json` was accepted for resume and remains the sole vendor-specific input; bounded source and tests reflect execution-2 changes.

Resume Status guides routing but is not Acceptance proof.

## Remaining Work

### R1 — Reconcile FPO-persisted vendor-contract Evidence

- [x] Complete
- Depends on / preserves: must satisfy CONTRACT Required Inputs and Acceptance A1 without using `tools/vendor_release_contract.py` as authority.

Verified / observed:
- Execution-2 observation (`P7A-I3-EXECUTION-2`): `phase7a/evidence/I3-research.json` has `accepted_for_resume: true` and supplies schema version 2, output field `track`, accepted `stable`/`canary` values, and input-order preservation.
- The supplied Evidence is sufficient for the required vendor-specific implementation choices; the parent-only snapshot was not used as authority.

### R2 — Implement the smallest contract-conforming manifest builder

- [x] Complete
- Depends on / preserves: R1; public `build_manifest(config)` interface; existing lightweight Python architecture; all CONTRACT Implementation Commitments.

Verified / observed:
- `src/manifest.py` now returns `schema_version: 2`, preserves `name` and `version`, maps input `channel` to `track`, accepts only `stable` or `canary`, and copies artifacts without reordering.

### R3 — Add focused source-bound tests and validate the Active Stage

- [x] Complete
- Depends on / preserves: R2; Acceptance A2–A6 and regression obligations; no weaker substitute for unknown vendor semantics.

Verified / observed:
- Focused tests cover exact schema-v2 output, both accepted tracks, rejection of an unknown track, artifact order, and equivalent-input determinism.
- `python -m unittest discover -s tests -v` via the bundled Python runtime: 4 tests passed.
- Direct public-callable validation: PASS for exact output, both tracks, nontrivial order, repeated equality, and input non-mutation.

Task split/order may adapt during Execution only when Stage, CONTRACT Implementation Commitments, and Acceptance proof subject/boundary/strength remain unchanged.

## Material Warnings / Carry-forward Facts

- The current implementation contains plausible defaults and ordering behavior, but these are Current Reality only and are not official-contract Evidence.
- The existing test observes only `name` and `version`; passing it cannot close the Stage.
- `tools/vendor_release_contract.py` is explicitly parent-only and must not be used as worker authority or as a substitute for FPO-persisted source-bound Evidence.

## References

- Normative current source: I3 bounded-project `README.md` → `phase7a/fixture/i3-external-gap/README.md` — reopen if source identity/content changes or Evidence appears to conflict.
- Fact/Evidence current source: implementation → `phase7a/fixture/i3-external-gap/src/manifest.py` — reopen before effects and after any source change/interruption.
- Fact/Evidence current source: tests → `phase7a/fixture/i3-external-gap/tests/test_manifest.py` — reopen before validation and after any test change.
- Fixed controller template: Flow Mini v0.5.0 candidate r3 → project-local `.flow-mini/EXECUTION.md` — replan if Controller Revision no longer matches CONTRACT.
- Required future input: FPO-persisted official vendor-contract Evidence → locator not yet available — reopen when FPO supplies a durable identity/locator.

## Final Evidence

- Execution-2: four-Core generation `P7A-I3-PLANNING-1-G1` remains coherent; persisted source-bound Evidence resolved the recorded input gap, the minimal implementation and focused tests are complete, and all implementation-local validation passed. FPO acceptance and close remain out of scope.
