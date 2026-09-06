# Fluid Progress Orchestration v0.2
## Architectural Hardening Candidate

Fluid Progress Orchestration（FPO）は、曖昧な要求から必要な調査・設計・実行・検証・回復を進め、機械で代替可能な判断を不要にHumanへ戻さず、bounded workを検証済み成果まで運ぶためのオーケストレーション方式です。

## このCandidateの姿

```text
6-checkpoint Achievement Plane
        +
小さいJ/P/M Policy Kernel
        +
外部Operational Records
  Definition / Plan / Work Control
  Operation / Blocker / Evidence / Effect
  Trust / Capability / Commit / Projection
```

Coreは仕事の成立条件とAuthorityだけを持ち、長い履歴、待機、Cancel、Budget、Agent状態、副作用、Evidenceは外部Recordへ分離します。

## 読む順番

1. `docs/CANDIDATE_STATUS.md` — 現在の判定と証明済み/未証明範囲
2. `docs/FPO_OVERVIEW.md` — 全体像と正確なClaim
3. `docs/ARCHITECTURE_DECISIONS.md` — なぜこの形か
4. `runtime/contracts/AUTHORITY_MATRIX.md` — 誰が何を決めるか
5. `docs/REFERENCE_FLOW.md` — 正常・Recovery・Cancelの流れ
6. `examples/canonical_work/README.md` — 中断状態の具体例
7. `validation/STATIC_INTEGRITY_CHECK.md` — 現在証明できた範囲

Runtimeの入口は `runtime/RUNTIME_ENTRY.md` です。`docs/`、`review/`、`validation/`、`examples/`、`extensions/` はRuntime Control Contextへ混ぜません。

## 検査

```bash
python validation/validate_candidate.py
```

検査対象はRuntime Manifest/hash、Authority、24種のimmutable Record、Dispatch/Return境界message、canonical fixture、commit digest、state vocabulary、64件の決定論的不変条件です。

## 現在のStatus

- Architecture / Contract: Candidate
- Static / Schema / Deterministic model: report参照
- Runtime E2E: **NOT EXECUTED**
- Autonomous completion / crash durability / prompt-injection resistance: **NOT PROVEN**

このBundleは長期実環境変更へそのまま投入するRuntimeではありません。次は `docs/NEXT_RUNTIME_PROBE.md` の極薄Sandbox ProbeでContractの実効性を確認します。
