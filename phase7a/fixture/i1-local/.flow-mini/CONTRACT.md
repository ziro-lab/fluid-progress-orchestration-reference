# CONTRACT

- Core Generation: P7A-I1-PLANNING-1-G1
- Controller Revision: FM-EXEC-0.5.0-r3

## Source Basis

- Current implementation source: `README.md` in the bounded I1 Label Slugger project, inspected at repository revision `fb74cac46a3833195262f6e4a3a78c3034b819a9`.
- Semantic role: `README.md` is Normative for the requested behavior and project boundary; `src/slugger.py` and `tests/test_slugger.py` are Fact/Evidence of Current Reality, not alternative requirements.
- Currentness basis: the assigned dispatch identifies this bounded project and asks for usability according to its project materials; no conflicting in-scope source was found.
- Durable locators: `README.md`, `src/slugger.py`, and `tests/test_slugger.py` relative to the bounded project root.
- Reopen trigger: a Material change to the README, public `build_slugs(labels)` interface, bounded project contents, or target revision before/during Execution.

## Goal Horizon / Normal Return

- Current authorized Goal Horizon: make the bounded label tool satisfy all behavior stated in `README.md`, validate the result, and report completion without modifying files outside this project.
- Normal Return Point: the implementation is minimal, all Active Stage Acceptance obligations have Current evidence, and the bounded project is ready for ordinary use through `build_slugs(labels)`.
- Remaining authorized Horizon after this Stage: none; this Active Stage covers the full current Horizon.

## Active Implementation Stage

- Stage: correct and validate the deterministic `build_slugs(labels)` behavior described by `README.md`.
- Entry basis: `src/slugger.py` currently sorts inputs by `str(item)` before enumeration; the existing implementation otherwise contains trimming, rejection, slug conversion, and result-shape logic. Existing tests already specify order/duplicate preservation and continuation after rejected items.
- Exit: all checks in `ACCEPTANCE.md` pass against the final bounded-project implementation, with no unrelated project changes.
- Preserve: the importable `build_slugs(labels)` function, the exact top-level `accepted`/`rejected` JSON-shaped result, accepted/rejected item shapes, deterministic behavior, and processing of later items after a rejection.

## Goal / User-facing Outcome

- Callers receive deterministic slugs and per-item rejection information in original input order, including duplicate labels, exactly as documented.

## Current Reality / Domain-Workflow Facts

- `src/slugger.py` enumerates `sorted(labels, key=lambda item: str(item))`, so accepted order and rejection indices can differ from original input order.
- The current regex `[^A-Za-z0-9]+` already represents runs of non-ASCII-alphanumeric characters, replacement with one hyphen, and boundary hyphen removal.
- Current tests cover accepted order/duplicates and rejection continuation/indexes, but do not cover all documented normalization and deterministic output constraints.
- Evidence basis: direct inspection of `README.md`, `src/slugger.py`, and `tests/test_slugger.py` at the revision above.

## Requirements / Settled Design

- `build_slugs(labels)` accepts a list of label values and returns exactly a mapping with `accepted` and `rejected` arrays.
- Process values in original list order and preserve duplicates.
- For each string, trim surrounding whitespace before further processing and retain that trimmed string as accepted-item `input`.
- Convert ASCII letters to lowercase, replace each run of characters outside ASCII letters/digits with one `-`, and remove leading/trailing `-` characters.
- Reject a non-string with its original zero-based index and a short reason; continue processing later values.
- Reject a string empty after trimming with its original zero-based index and a short reason; continue processing later values.
- Each accepted item contains exactly `input` and `slug`; each rejected item contains exactly `index` and `reason`.
- Do not add timestamps, random identifiers, environment-dependent fields, or other nondeterministic output.

## Constraints / Interfaces / Invariants

- Keep the existing public function name and single-argument interface.
- Do not modify files outside the bounded I1 project.
- Do not introduce a dependency or architectural layer for behavior achievable with the existing Python standard-library implementation.
- A trimmed non-empty string made entirely of non-ASCII-alphanumeric characters is accepted with an empty slug; rejection is limited to the two documented conditions.

## Implementation Commitments

- Retain a direct, deterministic, single-pass transformation over the caller-provided list; do not sort, deduplicate, or mutate the input.
- Use only Python standard-library capability already suitable for the bounded transformation; no new package or persistence/configuration surface.
- Make the smallest source/test changes needed for the documented contract, then validate the complete behavior and affected regressions before completion.
- Preserve original indices by enumerating the original input sequence; rejection must not stop or renumber subsequent processing.

## Required Inputs / Fixtures

- Existing `README.md` for the normative behavior.
- Existing `src/slugger.py` implementation target.
- Existing `tests/test_slugger.py` regression suite, extended only where needed to prove uncovered documented behavior.

## Risk / Delegation / Confirmation Boundary

- All planned effects are local, reversible edits within the bounded project. No destructive, external, costly, credentialed, or data-transmitting action is required.
- Execution may choose equivalent local edit/test mechanics, but changing the public interface, dependency basis, Active Stage, or proof boundary requires REPLAN.

## Future / Out

- CLI, packaging, persistence, locale-specific transliteration, Unicode alphanumeric preservation, uniqueness enforcement, and behavior for non-list top-level inputs are outside the current documented scope.
