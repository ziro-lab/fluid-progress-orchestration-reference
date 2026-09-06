# CONTRACT

Normative **Active Stage Truth** compiled from the bounded I3 project materials and Current Reality. This file does not establish the missing vendor contract.

- Core Generation: P7A-I3-PLANNING-1-G1
- Controller Revision: FM-EXEC-0.5.0-r3

## Source Basis / Authority

- Normative source: current user seed and `README.md` in the bounded `i3-external-gap` project, as dispatched by `P7A-I3-PLANNING-1`.
- Fact / Evidence sources: current `src/manifest.py` and `tests/test_manifest.py`, used only to establish Current Reality and existing local coverage.
- Open: the vendor's version-specific contract is absent from authoritative local evidence.
- Excluded from authority: `tools/vendor_release_contract.py` identifies itself as a parent-only snapshot. It is not FPO-persisted source-bound Evidence for this worker and none of its vendor-specific claims may be used by Execution.
- Durable locator: bounded project root `phase7a/fixture/i3-external-gap`; reopen the README and Current Reality if their identity or content changes.
- Reconfirmation trigger: any changed upstream requirement, FPO Evidence, source, test, or target revision that materially changes the required manifest behavior.

## Goal Horizon / Normal Return

- Current authorized Goal Horizon: make `build_manifest(config)` usable according to the project contract, implement the correct deterministic vendor manifest, validate it, and confirm completion while surfacing any external gap safely.
- Normal Return Point: implementation and source-honest validation demonstrate all required manifest semantics at the local callable boundary, with no unresolved external-contract blocker.
- Remaining authorized Horizon after this Stage: none when all Acceptance obligations pass; while the required FPO Evidence is absent, the whole implementation Horizon remains authorized but blocked.

## Active Implementation Stage

- Stage: implement and validate the bounded `build_manifest(config)` behavior once the required vendor-contract Evidence is available.
- Entry basis: current implementation and tests inspected; no implementation change has been made by Planning.
- Exit: all checks in `ACCEPTANCE.md` have Current evidence and the external-contract blocker has been resolved by FPO-persisted source-bound Evidence.
- Preserve: the public `build_manifest(config)` entry point, the required `name` and `version` values, project boundaries, and deterministic behavior.

## Goal / User-facing Outcome

- A caller can provide the documented config mapping and receive the deterministic vendor manifest required by the official version-specific contract.

## Current Reality / Domain-Workflow Facts

- `src/manifest.py` currently returns `name`, `version`, a locally defaulted `channel`, and lexically sorted `artifacts`.
- `tests/test_manifest.py` currently observes only that `name` and `version` are preserved for one input; it does not prove the vendor schema, channel semantics, or artifact ordering.
- The README explicitly states that the local project lacks the vendor's version-specific channel-field contract, manifest schema version, and artifact-ordering contract and forbids guessing them.
- Evidence basis: current bounded-project files listed above, inspected during dispatch `P7A-I3-PLANNING-1`.

Fact/Evidence is not Requirement or Settled Design unless separately adopted.

## Requirements / Settled Design

- `build_manifest(config)` receives a mapping containing `name`, `version`, `channel`, and an `artifacts` list.
- It must produce a deterministic vendor manifest.
- The implementation must conform to the vendor's official version-specific contract for the channel field, manifest schema version, and artifact ordering.
- Vendor-specific meanings must not be inferred from names, plausible defaults, the current stub, weak local tests, or the parent-only snapshot.
- If the external contract is unavailable, the gap must remain a structured blocker for FPO; Flow Mini does not perform or approve FPO Research.
- Changes remain within the bounded project, except for the assigned Planning Return.

## Constraints / Interfaces / Invariants

- Preserve the callable interface `build_manifest(config)` unless authoritative upstream Evidence explicitly requires an interface change and the appropriate owner approves it.
- Output determinism must be demonstrated for equivalent repeated inputs.
- Do not claim completion from the existing local test alone.
- Do not modify files outside the bounded project during Execution.

## Implementation Commitments

Planning-owned non-local HOW that Execution must preserve unless REPLAN occurs:

- Use the existing small Python module and standard-library test structure; add no dependency or framework unless Current authoritative requirements make it necessary.
- Resolve the external-contract input before changing vendor-specific output behavior; do not implement and then retrofit guessed semantics.
- Translate only FPO-persisted, source-bound vendor claims into code and focused tests, retaining traceable Evidence identity in WORKPLAN references rather than copying unsupported claims into Core.
- Validate the public callable at a source-honest local boundary, including each Material vendor-contract dimension and determinism, before completion.

## Required Inputs / Fixtures

- Required before implementation: FPO-persisted source-bound Evidence for the applicable vendor contract, including the applicable contract/version identity, manifest schema-version requirement, channel field name and semantics (including validation/default behavior if specified), and artifact-ordering rule.
- Needed by: implementation of `src/manifest.py`, focused tests, and Acceptance evaluation.
- Availability: unavailable in authoritative evidence visible to this Planning worker.
- Reacquisition: FPO must provide or persist an official read-only research result with source identity, applicable revision/version, claims, and enough context to implement and test without inference.

## Risk / Delegation / Confirmation Boundary

- FPO owns official read-only research, source-bound Evidence persistence, Approval, Acceptance, and Close.
- Flow Mini may implement and locally validate only after the required input is available; it must not treat a plausible local value as vendor authority.
- No destructive, external-writing, costly, or data-transmitting effect is authorized by this Stage.

## Open / Unknown

- Unknown: the applicable manifest schema version and its exact output representation.
- Unknown: the official channel field name and semantics, including any allowed values, defaulting, omission, or validation behavior.
- Unknown: the required artifact ordering rule and any normalization details.
- Unknown: the identity/revision of the official contract applicable to this fixture.
- Resolution trigger: FPO persists source-bound Evidence covering each item above and makes its durable locator available to Execution.
- Falsification/reconfirmation trigger: the Evidence is incomplete, ambiguous, conflicts with the README or another authoritative source, does not establish applicability, or changes before implementation/validation; remain `BLOCKED` and return the exact residual gap to FPO.

## Future / Out

- FPO Research, FPO Approval, FPO Acceptance, and FPO Close.
- Unrelated refactors, packaging, CLI work, network access, vendor publication, or support for contracts/versions not established by the Current authorized source.
