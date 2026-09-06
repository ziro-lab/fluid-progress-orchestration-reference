# ACCEPTANCE

Observable **proof obligations** for the Active Stage. Exact commands are guidance; equivalent or stronger source-honest methods at the same boundary are allowed.

- Core Generation: P7A-I2-PLANNING-2-d32fce32

## Acceptance Checks

### A1 — Stable badge follows the settled design

Observe:
- The real bounded-project `render_badge` function result for `("stable", "1.2.3")`.

Required boundary / strength:
- Direct unit/runtime observation of the actual implementation, without a mock or substitute.

Suggested method:
- Run the existing Python unit test for the stable case, or an equivalent direct call.

Expected:
- Exactly `{"text": "stable 1.2.3", "color": "green"}`.

Material dimensions:
- Channel variant: `stable`.

### A2 — Canary badge follows the settled design

Observe:
- The real bounded-project `render_badge` function result for `("canary", "1.2.3")`.

Required boundary / strength:
- Direct unit/runtime observation of the actual implementation, without a mock or substitute.

Suggested method:
- Run the existing Python unit test for the canary case, or an equivalent direct call.

Expected:
- Exactly `{"text": "canary 1.2.3", "color": "amber"}`.

Material dimensions:
- Channel variant: `canary`.

### A3 — Output is deterministic and preserves supplied badge text inputs

Observe:
- Repeated direct calls with identical settled-channel inputs produce identical dictionaries.
- For representative supplied version text, the output text contains the exact supplied channel label followed by the exact supplied version, with no replacement by `release` or another value.

Required boundary / strength:
- Direct unit/runtime observation of the actual implementation for both settled channel variants.

Suggested method:
- Add or perform focused direct-call checks using at least one version value in addition to the existing `1.2.3` examples, then run the bounded test suite.

Expected:
- Results are equal across repeated identical calls; stable and canary text is formed from the corresponding supplied channel and version values exactly as `<channel> <version>`.

Material dimensions:
- Channel variants: `stable` and `canary`.
- Version propagation: more than one representative string value across the Stage evidence.

## Regression Checks

- Run the complete bounded-project test suite after the implementation change; all existing tests pass.
- Confirm the returned object shape remains the two observable fields `text` and `color` for both settled variants.
