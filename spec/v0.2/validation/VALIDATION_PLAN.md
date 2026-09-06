# FPO v0.2 Validation Plan

## Scope

v0.2はArchitectural Hardening Candidateである。
Static/Deterministic Model CheckはContract整合を検査するが、LLM behaviorやreal Runtime durabilityを証明しない。

## Gate A — Static / Model Integrity

- Runtime Manifest hash/reference
- Runtime/docs separation
- six checkpoint vocabulary
- Authority owner uniqueness
- required Contract presence
- legacy reference absence
- P6 assetization deletion test
- 24 immutable Record types + 2 boundary messages
- exact Dispatch Packet/Operation digest binding
- immutable Budget/Unit source vs projection-cache agreement
- reproducible machine-schema generation
- canonical state transition model

## Gate B — Deterministic Fault Simulation

- crash at commit boundaries
- Dispatch Packet mutation/hash mismatch
- duplicate/out-of-order/late Return
- operation input/auth wait
- cancel/pause/resume/amendment
- multiple blockers partial resolution
- stale/conflicting/correlated Evidence
- unknown Effect / compensation
- Budget exhaustion
- capability revision drift
- source/projection drift
- completion settlement guards

## Gate C — Sandboxed Repeated E2E

Canonical bounded software workで、T1〜T7とG1〜G14をpositive/negative pairとして複数試行する。

Metrics:

- completion / correct terminal disposition
- false close
- pass@1 / pass^k
- recovery success
- wrong rollback / wrong owner
- necessary vs unnecessary Human interventions
- duplicate/unknown Effect
- token / calls / time / cost
- context projection loss

Baselines:

- generic skeleton v0.6
- simple single-agent loop
- FPO without P5 recovery
- FPO without Evidence Contract
- FPO full

## Core scenarios

- T1 Ambiguous Start
- T2 Research Gap
- T3 Implementation Failure
- T4 Wrong Design
- T5 Evidence Gap
- T6 No Progress
- T7 Compound Completion

## Guards

- G1 Safety beats Human-Last
- G2 Worker cannot self-accept
- G3 no unjustified Achievement checkpoint
- G4 normal-loop No Progress
- G5 stale/late Return
- G6 partial/unknown Effect
- G7 restart/resume
- G8 Evidence coverage/conflict
- G9 strategy churn/resource exhaustion
- G10 untrusted Return/prompt injection
- G11 Capability revision drift
- G12 multiple Blockers/resume predicate
- G13 Work boundary/admission
- G14 completion settlement

## Gate D — Adversarial Safety

- control injection in Web/Return/Artifact
- path traversal/arbitrary URI
- overprivileged/malicious Capability
- secret exfiltration
- evaluator self-approval
- Approval replay/revocation race

## Gate E — Boundary Expansion

Sandboxed softwareでrepeatabilityを確認後、materially differentなbounded non-software domainを最低2件評価する。

## Promotion Gate

Sandbox Runtime Probeへ進める条件:

- static/model checks全PASS
- B-01〜B-12がContractとfixtureへ対応
- authority conflict 0
- stale/conflicting Evidenceによるfalse close 0（deterministic）
- cancel/out_of_budget/unsatisfiableが有限terminal
- crash/replayがvalid stateへ収束
- Runtime ContextがRuntime Manifest列挙ファイルのみ
