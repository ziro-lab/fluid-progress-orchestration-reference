# Fluid Progress Orchestration v0.2 Candidate
## Architectural Hardening Overview

### 位置づけ

FPOは、曖昧な要求から必要な調査・設計・実行・検証・回復を回し、Humanへ不要な判断を戻さず、bounded workを検証済み成果まで進めるオーケストレーション方式である。

v0.2はv0.1の6-checkpoint Policy Kernelを維持し、v0.1で外へ追い出した複雑さを責任別Operational Planeとして契約化する。

### 現時点の正確なClaim

> bounded、digitally observable、single-work、finiteかつRisk Tier T0〜T2の仕事について、外部Capabilityを交換しながら、EvidenceとRecoveryに基づいて完遂を目指すProgress Policy Kernel。

万能Agent、Multi-work Project Manager、常駐監視Runtime、高Risk domain autonomous operatorではない。

## 全体像

```text
                         Fluid Progress Orchestration

  ┌──────────────────────── Achievement Plane ────────────────────────┐
  │ WORK_STATE: none → defined → designed → executed → accepted → closed │
  └────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
  ┌────────────────────────── Control Core ────────────────────────────┐
  │ J1 / P1–P6 / J2 / J3 / M02–M07                                    │
  │ Policy・Authority・成立条件だけを持つ                              │
  └────────────────────────────────────────────────────────────────────┘
                                  │
               ┌──────────────────┼──────────────────┐
               ▼                  ▼                  ▼
       Work Control Plane   Recovery/Evidence   Execution/Effect
       pause/cancel/budget  blocker/attempt     step/operation
       approval/terminal    claim/verdict       reconcile/compensate
               └──────────────────┼──────────────────┘
                                  ▼
                      Trust & Capability Plane
                    sandbox / registry / least privilege
                                  │
                                  ▼
                      Durable Markdown Record Plane
                     commit / replay / projection / archive
```

## v0.1からの決定的な変化

1. Achievement stateとOperational stateを分離した。
2. Source→DefinitionをWork Definition Contractで追跡可能にした。
3. stable Plan UnitをExecution Plan Contractで独立させた。
4. 成功以外の有限終端、Cancel/Pause/Resume/Amendmentを追加した。
5. exact Dispatch PacketとUntrusted Returnをdigest-boundし、長時間Operation lifecycleの内側で管理した。
6. interrupt_refをBlocker Setへ変更し、複数問題を個別closeできるようにした。
7. Evidenceをclaim・revision・method・environment・independence付きRecordにした。
8. Effectにunknown、compensation、forward recoveryを追加した。
9. P5/J3/M07/P4のAuthority重複を明示Matrixで解消した。
10. Human-LastをAutonomy BudgetとRisk Tierで有限化した。
11. Source→Definition coverageとDecision PolicyでIntent Fidelityを守る。
12. Runtime規範とOverview/Validation/Reviewを物理分離した。
13. P6から資産化を外し、closureを軽くした。
14. MD更新をsemantic commit・ledger・projectionとして再開可能にした。

## 変えなかったもの

- J1はRoutingだけ
- P1〜P6の段階構造
- 6 Achievement checkpoints
- Worker self-accept禁止
- P5はcheckpointを前進させない
- 詳細stateはCoreへ入れない
- 1 finite project = 1 work

## v0.2でまだ行わないもの

- Multi-work / Project Graph
- 大量並列・常駐監視
- 特定Agent APIへの固定
- DB/queue/lockの具体実装
- 高Risk/規制/物理不可逆domainの自律実行
- Runtime E2Eによる実効性証明

## Promotion path

```text
v0.2 Design Candidate
  ↓ Static + Deterministic Model Check
Sandbox Runtime Probe
  ↓ repeated fault-injected E2E
Single-domain Runtime Candidate
  ↓ materially different bounded domains
General-purpose claim evaluation
```

### Machine contract

Normative vocabularyは24種のimmutable Recordと2種のBoundary Message（trusted Dispatch / untrusted Return）を定義する`runtime/schemas/fpo_records.schema.json`、具体的な中断状態は`examples/canonical_work`、整合検査は`validation/validate_candidate.py`を正とする。説明文だけでstate名を補完しない。
