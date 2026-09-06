# ACCEPTANCE

- Core Generation: P7A-I1-PLANNING-1-G1

## Acceptance Checks

### A1 — Original order, duplicates, and exact accepted shape

Observe:
- The result of `build_slugs([" Beta Label ", "alpha", "alpha"])`.

Required boundary / strength:
- Executed Python unit test against the final `src/slugger.py` through its public function.

Expected:
- The top-level result has exactly `accepted` and `rejected` keys.
- `accepted` is exactly `[{"input": "Beta Label", "slug": "beta-label"}, {"input": "alpha", "slug": "alpha"}, {"input": "alpha", "slug": "alpha"}]` in that order, and `rejected` is empty.
- Every accepted item has exactly `input` and `slug` keys.

### A2 — Trimming and ASCII slug normalization

Observe:
- Representative string values covering surrounding whitespace, uppercase ASCII letters, multiple runs of spaces/punctuation, leading/trailing separators, digits, and non-ASCII characters.

Required boundary / strength:
- Executed Python unit tests against the final public function, with exact result assertions.

Expected:
- Surrounding whitespace is removed from each accepted `input` before slugging.
- ASCII letters are lowercase; each run outside `[A-Za-z0-9]` becomes one `-`; leading and trailing `-` are absent; ASCII digits are preserved.
- A trimmed non-empty punctuation/non-ASCII-only label is accepted and may have `slug: ""` rather than being rejected.

### A3 — Rejections use original indices and processing continues

Observe:
- A mixed-order input containing valid strings before, between, and after an empty-after-trimming string and a non-string, chosen so sorting would change positions.

Required boundary / strength:
- Executed Python unit test against the final public function with exact accepted and rejected arrays.

Expected:
- Non-strings and empty-after-trimming strings are the only rejected items.
- Rejected entries appear in original processing order, contain exactly `index` and `reason`, use original zero-based input indices, and have short non-empty reasons appropriate to the condition.
- Valid later values are still accepted in original order.

### A4 — Deterministic, environment-independent output

Observe:
- Two calls with the same representative input in the same final runtime test process, plus inspection of the complete returned structure.

Required boundary / strength:
- Executed unit test and final-source inspection.

Expected:
- Both results are equal and contain no timestamps, random identifiers, environment-derived values, or undocumented fields.

## Regression Checks

- Run the complete existing project test suite after changes; all pre-existing tests pass.
- Confirm the fix does not mutate the caller-provided list and does not deduplicate repeated labels.

## Delivery / First Run

- From the bounded project root, the full test suite executes against the final `src/slugger.py` and passes.
- A fresh Python process can import `build_slugs` from `src/slugger.py` using the project's existing test/import convention and obtain the documented result shape.
