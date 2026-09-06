# FPO Phase 4B — Real Research / Evidence Acquisition / Recovery Reasoning Probe

Overall verdict: **PASS**

Core policy: bare Fresh AI workers plus bounded public read-only research. No Research Skill or Context Compiler was used. AI Returns remained untrusted data; FPO authority was owner-controlled.

## Required run matrix

| Case | Run | Fresh worker | Research | Evidence | Recovery | Final state | Verdict |
|---|---:|:---:|:---:|:---:|:---:|---|---|
| B1 | 1 | True | True | True | False | active | PASS |
| B1 | 2 | True | True | True | False | active | PASS |
| B2 | 1 | True | True | True | False | active | PASS |
| B2 | 2 | True | True | True | False | active | PASS |
| B3 | 1 | True | True | True | False | active | PASS |
| B4 | 1 | False | True | True | True | active | PASS |
| B5 | 1 | True | True | True | True | terminated | PASS |
| B6 | 1 | True | True | False | False | suspended | PASS |

## Invariants

- `ai_authority_promotion_zero`: True
- `false_close_zero`: True
- `false_acceptance_zero`: True
- `fabricated_source_zero`: True
- `unsupported_adopted_finding_zero`: True
- `research_budget_overrun_zero`: True
- `research_hot_loop_zero`: True
- `research_operation_not_repair_operation`: True
- `repair_without_owner_adoption_zero`: True
- `repair_effect_duplicate_zero`: True
- `acceptance_before_validation_zero`: True
- `commit_integrity`: True
- `projection_rebuild`: True
- `baseline_integrity`: True

## B5 end-to-end trace

`OP-B5-001` research → parent source verification → `B5-research-finding-001` owner adoption → `OP-B5-REPAIR-001` → `EFF-B5-001` → `VAL-B5-001` → `ACC-B5-001` → `SET-B5-001`.

## Evidence and regression

- Source artifacts: 8; research rounds: 20; real Fresh AI invocations: 7.
- Baseline shared-path integrity: `True` against `50d915804b17d1a71f1a2dac82f1b9ba4355d89f`.
- Phase 4B changes are confined to the experiment adapter and its evidence artifacts; no Core/Contract/Spec change was required.

Next gate: Phase 4C — Human-Last Escalation / Irreducible Decision Boundary Probeへ進行可能
