# 03 — Existing FPO / Flow Mini Mapping v0.1.4.2

Status: **IMPLEMENTATION MAPPING**

This document prevents accidental creation of duplicate authoritative state.

# 1. Execution Binding source map

The binding is a normalized view over existing exact identities.

Typical sources:

| Concern | Existing owner/source |
|---|---|
| Definition identity | FPO Dispatch / owner-native Definition ref/revision |
| Plan identity | FPO Dispatch / Delegated Operation exact Plan ref/revision |
| Attempt identity | FPO Delegated Operation `attempt_id` |
| Target identity | FPO Dispatch / Delegated Operation target revision |
| Policy/approval | FPO Work Control / approval/policy revision |
| Capability identity | FPO capability id/revision + binding ref |
| Dispatch identity | trusted dispatch ref/digest |
| Flow Mini implementation basis | Flow Mini Core Generation + Controller Revision / exact binding |
| Provider physical child | attempt-rooted Provider mapping |
| Material observations | Provider/evidence/source refs only when Effect-safety material |

Do not promote the normalized view itself into an independent authority source.

# 2. FPO ownership preserved

FPO remains authoritative for:

- Definition / Plan / Policy,
- Work Control / Authority / Approval / Budget,
- Delegated Operation / attempt,
- Return adoption,
- Effect lifecycle / unknown / compensation / forward recovery,
- Evidence / Criteria Verdict / Acceptance,
- P5 recovery,
- semantic commit / replay.

Parallel/Profile must not duplicate these.

# 3. Flow Mini ownership preserved

Flow Mini remains authoritative for implementation-local:

- CONTRACT,
- ACCEPTANCE,
- WORKPLAN,
- Core Generation,
- Controller Revision,
- Fresh Planning→Execution boundary,
- local adaptation / REPLAN boundary.

Flow Mini `DONE` / `STAGE_ACCEPTED` is not FPO `accepted/closed`.

# 4. Provider ownership preserved

Provider owns physical mechanics:

- child process/remote-job mapping,
- spawn reconciliation,
- effect mediation path,
- settlement proof,
- fencing/serialization,
- slot occupancy,
- physical freeze/publication.

Provider child success is neither FPO adoption nor Mutation Closure.

# 5. Model Policy ownership

Model placement/reasoning effort is operational policy only.

Model changes are not Authority changes and are not material Progress by themselves.
