# CONTRACT

Normative **Active Stage Truth** compiled from the current owner resolution and the bounded project reality. This file does not replace the upstream design source.

- Core Generation: P7A-I2-PLANNING-2-d32fce32
- Controller Revision: FM-EXEC-0.5.0-r3

## Source Basis / Authority

- Normative project requirements: `README.md` (current bounded-project brief) — `render_badge(channel, version)` returns `{text, color}`, is deterministic, and does not invent a channel or version.
- Normative settled design: `design/owner-resolution.md` (current owner resolution for this implementation stage) — use channel-label text; `stable` maps to `green`; `canary` maps to `amber`.
- Currentness evidence: `phase7a/evidence/I2-design-resolution.json`, schema `fpo.phase7a.design-resolution.v1`, identifies the owner resolution above after parent Design re-entry.
- Fact / Evidence: `src/badge.py` and `tests/test_badge.py` describe current implementation and executable expectations; they do not supersede the owner resolution.
- Reference / Suggestion: `design/brief-release.md` and `design/brief-channel.md` are not independently authoritative where they conflict; the current owner resolution supplies precedence for this Stage.
- Durable locator: the bounded project files listed above and `phase7a/evidence/I2-design-resolution.json` in the shared repository.
- Reopen / reconfirmation trigger: reopen Design only if the owner resolution is withdrawn, superseded, or implementation requires product semantics not settled there.

## Goal Horizon / Normal Return

- Current authorized Goal Horizon: make the bounded release-badge function usable according to the current project requirements and settled owner design, validate it, and report completion.
- Normal Return Point: the implementation satisfies all Stage proof obligations with current evidence and no unresolved Material blocker.
- Remaining authorized Horizon after this Stage: none; this small coherent Stage covers the current Horizon.

## Active Implementation Stage

- Stage / Waypoint: align the existing `render_badge` implementation with the settled stable and canary badge behavior and validate the bounded project.
- Entry basis: the function currently always returns `release <version>` with `blue`, while current tests expect channel-label text and channel-specific colors.
- Exit: all Acceptance checks have source-honest current evidence for the bounded project.
- Preserve: the public `render_badge(channel, version)` call shape, the `{text, color}` result shape, determinism, and direct use of caller-supplied channel/version values.

## Goal / User-facing Outcome

- A caller receives `stable <version>` in green for stable releases and `canary <version>` in amber for canary releases, without substituted channel or version text.

## Current Reality / Domain-Workflow Facts

- `src/badge.py` contains a small dependency-free Python function whose current constant release/blue behavior contradicts the settled design.
- `tests/test_badge.py` already contains unit examples for stable and canary with version `1.2.3`.
- No populated `.flow-mini/` Core existed before this Planning materialization.
- Evidence basis / locator: bounded project `src/badge.py`, `tests/test_badge.py`, and the project file inventory inspected during Planning.

## Requirements / Settled Design

- `render_badge(channel, version)` returns a dictionary with exactly the observable badge fields `text` and `color`.
- For channel `stable`, text is `stable <version>` and color is `green`.
- For channel `canary`, text is `canary <version>` and color is `amber`.
- Output is deterministic for the same inputs.
- Badge text uses the caller-supplied channel label and version; it must not substitute or invent either value.

## Constraints / Interfaces / Invariants

- Keep work inside the bounded project and avoid unrelated refactors.
- Do not add behavior claims for channels or input types not settled by the current sources.
- Do not change upstream Goal, Requirements, Scope, Settled Design, proof meaning, or owner precedence during Execution.

## Implementation Commitments

- Preserve the existing dependency-free function boundary and use the smallest local implementation needed; no new framework, package, persistence, I/O, or abstraction is justified.
- Limit implementation effects to bounded source/test material required by this Stage; preserve unrelated workspace state.
- Validate both settled channel variants and direct propagation of supplied version text before claiming the Stage complete.

## Required Inputs / Fixtures

- Existing bounded `src/badge.py` and `tests/test_badge.py`; both are present.
- Current owner resolution at `design/owner-resolution.md`; present and corroborated by the parent-supplied design-resolution evidence.

## Risk / Delegation / Confirmation Boundary

- Execution may choose reversible local code and test mechanics, but changing supported-channel semantics, fallback/error behavior, the Stage boundary, dependency basis, or proof strength requires the corresponding Planning or Design re-entry.

## Open / Unknown

- Behavior for channels other than `stable` and `canary`, and validation/coercion rules for unusual input types, are not settled by the current design.
- Resolution / falsification / reconfirmation trigger: do not invent those semantics; request Design re-entry only if they become necessary to satisfy the authorized Stage.

## Future / Out

- Additional release channels, input-validation policy, presentation formats, packaging, CLI/UI work, and broader refactoring are outside the current authorized scope.
