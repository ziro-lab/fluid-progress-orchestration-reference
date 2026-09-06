# Migration from FPO v0.1 Candidate

## Independent candidate

v0.1を上書きしない。v0.2はArchitectural Hardening forkとして扱う。
進行中workへBundleを混在させず、新workまたは明示Migration Recordで切り替える。

## File changes

| v0.1 | v0.2 |
|---|---|
| `DISPATCH_RETURN_CONTRACT.md` | `DELEGATED_OPERATION_CONTRACT.md` |
| `CAPABILITY_REGISTRY_CONTRACT.md` | `TRUST_AND_CAPABILITY_CONTRACT.md` |
| `P5_修正・例外ハーネス.md` | `P5_進行回復ハーネス.md` |
| `J3_P5回復経路判断ハーネス.md` | `J3_P5必要知識・能力判断ハーネス.md` |
| `M07_例外・引き継ぎ.md` | `M07_回復・引き継ぎ.md` |
| `P6_終了・資産化ハーネス.md` | `P6_終了・引き渡しハーネス.md` |
| `STATIC_REVIEW.md` | `validation/STATIC_INTEGRITY_CHECK.md` |
| P1内のdefinition規則 | `WORK_DEFINITION_CONTRACT.md` |
| P2/P3内のstep規則 | `EXECUTION_PLAN_CONTRACT.md` |
| Runtime/docs混在 | `runtime/`, `docs/`, `validation/`, `extensions/` 分離 |

## State changes

- WORK_STATEの形は維持し、`state_revision`と`current_commit_id`は`current_projection`へ置く
- `interrupt_ref` はsingle blockerではなくBlocker Setを指す
- Work Control、Operation、Evidence、Effectは外部Operational stateとして追加
- 新Achievement checkpointは追加しない

## Behavioral changes

- Work Control inactive時はJ1を起動しない
- P5はTarget/Designを直接変更しない
- P4のrollbackはValidation Method / Execution Planに事前定義されたrouteだけ
- P6はassetizationなしでclose可能
- success以外はWork Control terminal dispositionで有限終了
- Return/EvidenceはUntrusted Inbox→owner adoptionを必須化
