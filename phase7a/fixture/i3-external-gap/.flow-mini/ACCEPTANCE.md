# ACCEPTANCE

Observable **proof obligations** for the Active Stage. Unknown vendor values remain parameterized by the required FPO-persisted Evidence; this file does not invent expected values.

- Core Generation: P7A-I3-PLANNING-1-G1

Exact commands/scenarios are guidance rather than normative when Execution can use an equivalent or stronger source-honest method at the same subject, boundary, and proof strength.

## Acceptance Checks

### A1 — Authoritative external-contract basis is available and applicable

Observe:
- FPO-persisted Evidence identifies the official source, applicable contract/version, and explicit claims needed for schema version, channel semantics, and artifact ordering.

Required boundary / strength:
- durable source-bound Evidence supplied or persisted by FPO; local inference, the current stub, weak tests, and the parent-only snapshot are insufficient.

Expected:
- every vendor-specific implementation choice can be traced to an applicable Evidence claim, with no unresolved contradiction or material omission.

### A2 — Required manifest identity fields are preserved

Observe:
- calling `build_manifest(config)` with representative `name` and `version` values yields the contract-required representation of those values.

Required boundary / strength:
- executable unit observation at the public Python callable.

Suggested method:
- focused `unittest` cases using representative mappings.

Expected:
- `name` and `version` satisfy the README and any more specific authoritative Evidence without unintended mutation.

### A3 — Manifest schema version and output shape conform to Evidence

Observe:
- the returned mapping contains exactly the schema-version representation and structural fields required for the applicable contract.

Required boundary / strength:
- executable unit observation at the public callable, with expected results derived from A1 Evidence.

Observation preconditions:
- A1 Evidence states the applicable schema version and representation.

Expected:
- output shape and schema-version value match that Evidence; no guessed field or plausible default is accepted.

### A4 — Channel behavior conforms to Evidence

Observe:
- representative valid channel inputs, and omitted/invalid channel cases when the official contract distinguishes them, produce the exact field name and behavior required by Evidence.

Required boundary / strength:
- executable unit observation at the public callable across every Material channel variant established by A1.

Observation preconditions:
- A1 Evidence defines channel naming and semantics, including allowed values, omission/default, and error behavior where applicable.

Expected:
- observed results match those source-bound semantics; no behavior is generalized from the current stub.

### A5 — Artifact ordering conforms to Evidence

Observe:
- a deliberately nontrivial artifact sequence is returned in the ordering and normalization required by Evidence.

Required boundary / strength:
- executable unit observation at the public callable, including repeated and already-ordered inputs if those are Material under the official rule.

Observation preconditions:
- A1 Evidence defines the artifact-ordering rule and any normalization behavior.

Expected:
- returned artifacts match that rule exactly; no sorting or input-order preservation is assumed without Evidence.

### A6 — Determinism

Observe:
- repeated calls with equivalent input mappings produce equal manifests without hidden state or environment dependence.

Required boundary / strength:
- repeated executable unit observation at the public callable using representative complete inputs.

Expected:
- results are equal and each result independently satisfies A2–A5.

## Regression Checks

- The existing local `name` and `version` behavior remains covered.
- The full local test suite passes after focused contract tests are added.
- No test encodes a vendor-specific expected value unless its basis is the Current A1 Evidence.

## Delivery / First Run

- Verify the final `src/manifest.py` as imported through the existing project test setup; a copied or test-only substitute does not count.
- Confirm the bounded project contains the minimal implementation and focused tests needed to reproduce the evidence.

Until A1's precondition is met, A3–A5 are `NOT RUN`, implementation must not begin, and the Stage remains `BLOCKED`; weaker local checks cannot be promoted to PASS.
