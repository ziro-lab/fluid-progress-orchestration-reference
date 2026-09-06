# WORKPLAN

- Core Generation: P7A-I1-PLANNING-1-G1

## Current Resume

- Resume Status: DONE
- Current focus: implementation-local validation is complete for the bounded `build_slugs(labels)` stage.
- Next safe action: FPO may inspect the candidate Return; no further implementation action is required in this stage.
- Evidence subject/currentness: final bounded-project working tree based on repository revision `fb74cac46a3833195262f6e4a3a78c3034b819a9`, with implementation and focused regression tests updated in this execution.

Resume Status guides routing but is not Acceptance proof.

## Remaining Work

### R1 — Reconcile and correct original-order processing

- [x] Complete
- Depends on / preserves: public `build_slugs(labels)` interface, original indices, duplicates, continuation after rejection, and standard-library-only implementation.

Verified / observed:
- Final `src/slugger.py` enumerates the caller-provided `labels` directly, preserving original order, duplicates, and original rejection indices without mutating input.

### R2 — Complete focused regression coverage

- [x] Complete
- Depends on / preserves: all documented requirements and exact result item shapes without expanding product scope.

Verified / observed:
- `tests/test_slugger.py` covers order/duplicates, rejection continuation and exact entries, documented normalization including punctuation/non-ASCII-only input, exact shapes, determinism, and input non-mutation.

### R3 — Validate and compact final evidence

- [x] Complete
- Depends on / preserves: all Acceptance proof subjects and boundaries in `ACCEPTANCE.md`.

Verified / observed:
- Full suite from the bounded project root passed: `Ran 4 tests ... OK`.
- A fresh Python 3.12 process passed exact A1-A4 assertions, including the documented result shapes and fresh import through `src`.
- Final source inspection found no sorting, randomness, timestamps, or environment-derived fields; changes remain bounded to implementation, focused tests, WORKPLAN, and the assigned Return artifact.

Task split/order may adapt during Execution only when Stage, CONTRACT Implementation Commitments, and Acceptance proof subject/boundary/strength remain unchanged.

## Material Warnings / Carry-forward Facts

- Sorting by `str(item)` is the confirmed mismatch that can alter both accepted order and rejected original indices; reconcile the final implementation directly rather than assuming this is the only possible current change.
- Do not infer that an empty generated slug is a rejection: the source rejects only non-strings and strings empty after trimming.

## References

- Normative source: bounded I1 `README.md` at planning revision `fb74cac46a3833195262f6e4a3a78c3034b819a9` → `README.md` — reopen if the file, dispatch target, or implementation behavior materially changes.
- Fact/Evidence: current implementation → `src/slugger.py` — reopen at Execution activation and after interruption or edits.
- Fact/Evidence: current regression suite → `tests/test_slugger.py` — reopen before test changes and final validation.
- Fixed controller: Flow Mini v0.5.0 candidate r3 template → `.flow-mini/EXECUTION.md` — verify its header remains `FM-EXEC-0.5.0-r3` before any effect.

## Final Evidence

- Core Generation remains `P7A-I1-PLANNING-1-G1`; the fixed `EXECUTION.md` remains unchanged.
- Implementation-local result: `DONE` for this Flow Mini execution only. FPO acceptance and close are not claimed.
- Validation command: `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests -v` → 4 tests passed.
- Fresh-process focused validation → `A1-A4 fresh-process validation: PASS`.
