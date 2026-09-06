# FPO v0.2 Deletion and Compression Review

## 目的

必要な意味を落とさず、Core・Runtime Context・契約数を最小にする。

## Coreに追加しなかったもの

- 新しいAchievement checkpoint
- Research専用P段階
- Evidence専用P段階
- WAIT / FAILED / CANCELED / NO_PROGRESS state
- Multi-work Project Manager
- Capability固有Agent名
- DB / queue / lock / provider API実装

これらは既存P/J/M、外部Operational Record、または将来Runtimeへ配置できるため、Core追加は棄却した。

## 統合したもの

| 旧分離案 | v0.2 | 理由 |
|---|---|---|
| Capability Registry + Trust | Trust and Capability Contract | Capability選定と権限・identityを分離すると過剰権限を見逃す |
| Dispatch + Returnの単発完了モデル | Delegated Operation Contract | exact Packet/Return digestを残しつつ、長時間state、cancel、unknown、stale updateを一つのlifecycleで扱う |
| Retry履歴 + No Progress state | Active Blocker + Progress Claim | 活動量ではなくBlocker単位のnet progressを見る |
| Assetization in P6 | Optional extension | 成果完遂のcritical pathではない |

## 統合しなかったもの

| Contract | 統合しない理由 |
|---|---|
| Work Definition | P1 AuthorityとIntent Fidelityを守る |
| Execution Plan | P2 Authorityとpartial resumeを守る |
| Work Control | User/Runtime lifecycleでありJ/P achievementとは別 |
| Delegated Operation | Provider task state。Effect成立とは別 |
| Active Blocker | P5のcase/rollback authorityを保持 |
| Evidence | P4 acceptanceとstaleness/independenceを保持 |
| Effect Recovery | 現実世界の変更・補償をOperationから分離 |
| Trust and Capability | 外部入力・権限境界を横断的に強制 |
| Runtime Contract | commit/replayというmechanism invariantを保持 |
| Authority Matrix | 重複責任を一か所で検出する正本 |

## Runtime Context削減

LLM Control Contextへ常時入れるのは、Entry、最小核、current projection、J1、現在のowner stageと選択済みM/Contractだけ。

次は常時ロードしない。

- JSON Schema全文（validatorのみ）
- Overview / ADR / Migration
- Validation / Review / Fixtures
- Assetization extension
- 全履歴・raw Evidence・Untrusted Inbox

## 結論

v0.2はv0.1よりファイルが増えるが、Coreの責任は増やしていない。増加分は、v0.1で暗黙だった外部状態を責任別に明文化したもの。

削除すると事故が再発する契約だけを残し、具体Runtime実装は依然として外へ出している。
