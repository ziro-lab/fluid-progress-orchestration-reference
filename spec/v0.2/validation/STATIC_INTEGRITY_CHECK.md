# FPO v0.2 Static Integrity Check

## Status: **PASS**

This proves static identity, schema/fixture consistency, and deterministic invariants only. Runtime behavior remains unproven until sandbox E2E.

## Static checks

| ID | Status | Detail |
|---|---|---|
| S-01 | PASS | Runtime Manifest parsed: 29 entries |
| S-02 | PASS | Manifest exactly covers all normative runtime Markdown/JSON files |
| S-03 | PASS | Runtime file hashes match |
| S-04 | PASS | Runtime and development contexts are physically separated |
| S-05 | PASS | All hardening core/contracts/schema are present |
| S-06 | PASS | No legacy normative references |
| S-07 | PASS | Runtime Markdown/JSON references resolve |
| S-08 | PASS | Six Achievement checkpoints preserved |
| S-09 | PASS | Critical Authority owners are explicit and non-conflicting |
| S-10 | PASS | Operational contracts declare contract 0.2 |
| S-11 | PASS | P5 target-mutation and forward-checkpoint guards present |
| S-12 | PASS | Closure is settled without assetization and terminates Work Control |
| S-13 | PASS | All BLOCKER/HIGH review findings mapped |
| S-14 | PASS | JSON Schema valid with 24 record types + 2 boundary messages |
| S-15 | PASS | Canonical fixtures schema-valid (26) and boundary-message control injection rejected |
| S-16 | PASS | Canonical semantic Commit covers and hashes all adopted fixture inputs |
| S-17 | PASS | Contract and machine-schema state vocabularies align |
| S-18 | PASS | Risk Tier T0–T3 and T3 autonomy boundary are normative |
| S-19 | PASS | No obsolete v0.1 operational vocabulary outside frozen review |
| S-20 | PASS | Full immutable bundle manifest matches (generated reports excluded by contract) |
| S-21 | PASS | Trust zones, schema gate, least privilege, secret handles, sandbox, and egress controls are normative |
| S-22 | PASS | Intent Fidelity has immutable source, coverage, assumptions, discretion, and decision policy |
| S-23 | PASS | Runtime Control Context excludes development/review/fixture material and full schema loading |
| S-24 | PASS | Canonical outbound Dispatch Packet is schema-valid, identity-matched, and digest-bound to Operation |
| S-25 | PASS | Immutable Budget/Unit records are the source; Work Control/Current Projection caches agree |
| S-26 | PASS | Normative JSON Schema is reproducibly generated from checked-in source |
| S-27 | PASS | Contradictory lifecycle, Evidence, Effect, Approval, admission, and settlement records fail schema validation |
| S-28 | PASS | Canonical fixture forms one digest-bound, authority-consistent operational graph |
| S-29 | PASS | Source→Definition→Plan→Validation traceability is exact for the canonical work |
| S-30 | PASS | P1 fidelity, P2 conditional Effect recovery, and P6 settlement-failure authority guards are normative |

## Deterministic model

| ID | Status | Invariant |
|---|---|---|
| M-01 | PASS | J1 six-checkpoint routing |
| M-02 | PASS | Suspended Work Control blocks J1 |
| M-03 | PASS | Active blocker routes P5 |
| M-04 | PASS | Pending cancel/amendment blocks J1 |
| M-05 | PASS | Unknown Achievement state fails closed |
| M-06 | PASS | Pause/resume lifecycle |
| M-07 | PASS | Finite cancel lifecycle |
| M-08 | PASS | Terminal work cannot silently resume |
| M-09 | PASS | Immediate provider success is legal |
| M-10 | PASS | Unknown Operation reconciles to observed terminal |
| M-11 | PASS | Terminal Operation cannot restart |
| M-12 | PASS | Unknown Operation prevents duplicate retry |
| M-13 | PASS | Current ordered Return is adoptable |
| M-14 | PASS | Stale Return is rejected |
| M-15 | PASS | Capability revision drift is rejected |
| M-16 | PASS | Duplicate/out-of-order Return is rejected |
| M-17 | PASS | Partial blocker resolution keeps set open |
| M-18 | PASS | All blockers resolved/superseded clear set |
| M-19 | PASS | One waiting blocker does not freeze other diagnosable blockers |
| M-20 | PASS | All blocking work waiting causes suspend |
| M-21 | PASS | P4 may apply predefined validation route |
| M-22 | PASS | P4 cannot invent rollback route |
| M-23 | PASS | Target mutation returns to P3 authority |
| M-24 | PASS | Design mutation returns to P2 authority |
| M-25 | PASS | Definition invalidation returns to P1 authority |
| M-26 | PASS | Evidence-only recovery may retain executed |
| M-27 | PASS | UNKNOWN criterion prevents Acceptance |
| M-28 | PASS | Contradictory Evidence prevents Acceptance |
| M-29 | PASS | Stale Evidence prevents Acceptance |
| M-30 | PASS | Partial coverage prevents Acceptance |
| M-31 | PASS | Correlated-only Evidence is not an independent check |
| M-32 | PASS | Current independent Evidence can pass |
| M-33 | PASS | Unknown Effect prevents retry |
| M-34 | PASS | Confirmed Effect is not duplicated |
| M-35 | PASS | Compensated Effect may permit a new attempt |
| M-36 | PASS | Crash before Commit ignores staging |
| M-37 | PASS | Commit before alias update rebuilds new projection |
| M-38 | PASS | Uncommitted alias is rejected |
| M-39 | PASS | Inflight Operation blocks closure |
| M-40 | PASS | Unsettled Effect blocks closure |
| M-41 | PASS | Completion settlement can close |
| M-42 | PASS | Successful terminal aligns closed/completed |
| M-43 | PASS | Canceled terminal preserves last valid Achievement |
| M-44 | PASS | Non-success terminal cannot claim closed |
| M-45 | PASS | Bounded T1 digital work is admissible |
| M-46 | PASS | T2 requires explicit controls |
| M-47 | PASS | Controlled T2 may be admitted within scope |
| M-48 | PASS | T3 is outside autonomous P3 scope |
| M-49 | PASS | Open-ended monitoring is rejected/split |
| M-50 | PASS | Complete source coverage can promote Definition |
| M-51 | PASS | Dropped source clause prevents defined |
| M-52 | PASS | Unresolved blocker prevents defined |
| M-53 | PASS | Resume only unfinished units |
| M-54 | PASS | Dependency invalidation reruns only affected unit |
| M-55 | PASS | Exact Dispatch digest and identity binding is accepted |
| M-56 | PASS | Mutated Dispatch digest is rejected |
| M-57 | PASS | Immutable Budget/Unit sources can agree with current projection caches |
| M-58 | PASS | Projection/source drift is rejected |
| M-59 | PASS | Activity or strategy churn alone is not Progress |
| M-60 | PASS | Adopted material net improvement is Progress |
| M-61 | PASS | Hard autonomy budget stops further execution |
| M-62 | PASS | Provider success without P3 adoption cannot promote executed |
| M-63 | PASS | Capability Return digest mismatch prevents adoption |
| M-64 | PASS | P6 settlement failure routes through Active Blocker rather than direct rollback |

## Explicitly not proven

- autonomous completion quality
- root-cause accuracy on long LLM traces
- real crash durability and concurrency
- prompt-injection resistance
- repeated E2E reliability/cost
- non-software generality
