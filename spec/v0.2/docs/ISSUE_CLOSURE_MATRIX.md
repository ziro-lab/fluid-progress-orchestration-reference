# FPO v0.2 Issue Closure Matrix

## BLOCKER findings

| ID | Design response | Normative location | Status |
|---|---|---|---|
| B-01 Operation lifecycle | exact Dispatch Packet/Return digest、nonterminal/terminal、lease、cancel、stale Return | Delegated Operation Contract | CONTRACT ADDRESSED / runtime proof pending |
| B-02 finite non-success terminal | Work Control terminal disposition | Work Control Contract | CONTRACT ADDRESSED |
| B-03 multiple blockers | Blocker Set + per-case lifecycle | Active Blocker Contract | CONTRACT ADDRESSED |
| B-04 durable commit/replay | commit ledger、projection rebuild、orphan semantics | 実行基盤契約 | CONTRACT ADDRESSED |
| B-05 trust boundary | zones、inbox、schema、least privilege | Trust and Capability Contract | CONTRACT ADDRESSED / adversarial proof pending |
| B-06 evidence contract | claim/revision/method/freshness/independence | Evidence Contract | CONTRACT ADDRESSED |
| B-07 effect compensation | unknown/reconcile/compensate/forward recovery | Effect Recovery Contract | CONTRACT ADDRESSED |
| B-08 authority overlap | explicit owner matrix + core rewrite | Authority Matrix | CONTRACT ADDRESSED |
| B-09 autonomy budget | immutable resource_budget + Work Control cache + M07 policy | Work Control / M07 | CONTRACT ADDRESSED |
| B-10 intent fidelity | source coverage、Decision Policy、assumptions | Work Definition Contract / P1 | CONTRACT ADDRESSED |
| B-11 user control/approval | Control Event + Approval lifecycle | Work Control Contract | CONTRACT ADDRESSED |
| B-12 runtime/dev mixing | Runtime Manifest and directory separation | Runtime Manifest | CONTRACT ADDRESSED |

## HIGH findings

| ID | Response | Status |
|---|---|---|
| H-01 Progress Goodhart | net adopted Progress Claim | CONTRACT ADDRESSED |
| H-02 root cause lifecycle | symptom / earliest error / contributing cause / detection gap | CONTRACT ADDRESSED |
| H-03 capability fitness | health/trust/cost/cancel/eval/risk | CONTRACT ADDRESSED |
| H-04 partial execution/resume | stable Plan Unit + immutable plan_unit_state + projection cache | Execution Plan Contract | CONTRACT ADDRESSED |
| H-05 context projection | WORK_INDEX + source refs + loss check | CONTRACT ADDRESSED |
| H-06 evaluation weakness | repeated/fault/adversarial/baseline gates | CONTRACT ADDRESSED / execution pending |
| H-07 method self-justification | method equivalence record and P2 ownership | CONTRACT ADDRESSED |
| H-08 risk tier | T0–T3 and approval gates | CONTRACT ADDRESSED |
| H-09 assetization critical path | extensionへ移動 | CONTRACT ADDRESSED |
| H-10 global blocker | scopeを記録。v0.2ではnormal routing global stopを維持 | ACCEPTED LIMITATION |

## Remaining proof obligations

- Runtime implementationがContractを遵守するか
- crash pointごとのdurability
- prompt injection / malicious Capability耐性
- repeated E2EでHuman interventionとfalse closeが減るか
- one-work境界が実案件で肥大化しないか
- non-software domainへの一般化
