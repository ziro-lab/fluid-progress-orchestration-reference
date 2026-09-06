# FPO v0.2 Multiangle Review
## 多角マップ v0.4.4適用 — Architectural Hardening再統合

## 判定

**DESIGN GO / SANDBOX RUNTIME PROBE READY WHEN STATIC GATE PASSES**

v0.1で見つかった主問題はControl Core不足ではなく、外部へ退避したOperational stateの未契約だった。v0.2は6-checkpoint Coreを維持し、責任別Contractとmachine schemaでその穴を閉じた。

ただし、Runtime E2E、実crash durability、adversarial security、反復信頼性は未証明である。

## 1. 目的・境界

**Status: PASS WITH EXPLICIT LIMITS**

- Claimをbounded / digitally observable / finite / single-work / T0–T2へ限定した。
- T3、常駐監視、Multi-work、無制約物理操作をadmission外とした。
- 成功以外のfinite terminalをWork Controlへ置いた。

残存証明: 実案件でsingle-workが肥大化しないか。

## 2. Achievement stateとOperational state

**Status: PASS**

- Achievementは6 checkpointのみ。
- pause/cancel/terminal、Operation、Blocker、Evidence、Effect、Budgetを外部Planeへ分離。
- Dispatch/Return本文をOperationへdigest bindingし、Unit/Budget source Recordとprojection cacheを一意化。
- `WORK_STATE`はBlocker Set refだけを持ち、詳細を抱えない。

削除テスト: WAIT / FAILED / CANCELED / NO_PROGRESS checkpointは不要。

## 3. Authority・User control

**Status: PASS**

- P1 Definition、P2 Design、P3 Target/Execution adoption、P4 Verdict/Acceptance、P5 Blocker/Rollback、P6 Closureを一意化。
- J3は分類、M07は継続Policyに限定。
- pause/resume/cancel/amendment/approval revokeはWork Control event。
- CapabilityはControl stateを変更できない。

残存証明: race条件下のapproval revocation/cancel伝播。

## 4. 失敗診断・Recovery

**Status: DESIGN PASS / RUNTIME PROOF PENDING**

- Blocker Setで複数問題、依存、waiting、部分解消を保持。
- symptom / earliest unrepaired error / contributing factor / detection gapを分離。
- Progressをactivityではなくadopted net improvementとして定義。
- Targetを変えたらP3、Designを変えたらP2へ戻す。

残存証明: 長いAgent軌跡でのroot-cause accuracyとwrong rollback率。

## 5. Evidence・評価

**Status: DESIGN PASS / REPEATED EVAL PENDING**

- claim、criterion、method、object/environment revision、freshness、coverage、lineage、independenceをSchema化。
- stale / conflicting / correlated-only / partial Evidenceでcloseしない。
- Validation method変更はP2 Authorityで、変更後methodだけによる自己正当化を禁止。
- pass@1だけでなくpass^k、false-close、wrong-owner、Human介入、costを測る。

残存証明: Sandboxed repeated E2E。

## 6. Security・Trust

**Status: DESIGN PASS / ADVERSARIAL PROOF PENDING**

- Trusted Control / Task / Evidence / Untrusted Inbox / Secret Storeを分離。
- Schema-valid Return、owner adoption、least privilege、path/egress scope、secret handleを要求。
- unknown control fieldをSchema errorとして拒否。
- ledger eventにhidden reasoningを保存しない。

残存証明: indirect prompt injection、malicious Capability、path traversal、secret exfiltration。

## 7. 資源・Context・Liveness

**Status: PASS**

- attempt、strategy family、time、token、cost、Tool/Research/Capability、Effect、Context Budgetを分離。
- Hard limitで停止または明示Approvalへ移る。
- Context projectionは再構築可能で、source refsとcoverage checkを要求。
- strategy churnだけをProgressとしない。

残存証明: 実測costとdiminishing-return threshold。

## 8. 運用・保守・Migration

**Status: DESIGN PASS / IMPLEMENTATION PROOF PENDING**

- append-only record、semantic commit、CAS、projection rebuild、orphan semanticsを規定。
- Runtime Manifestで規範Contextを限定。
- v0.1と混在させず明示Migrationとする。
- closure後のassetizationをoptional extensionへ分離。

残存証明: 全write boundaryのcrash injectionとschema migration。

## 9. 重複・圧縮・不要化

**Status: PASS**

削除・統合したもの:

- Registry単独Contract → Trust & Capabilityへ統合
- Dispatch/Returnの単発完了モデル → exact Dispatch Packet + Untrusted Returnを含むDelegated Operation lifecycleへ置換
- P5のTarget修正責務 → P3へ返却
- P6 mandatory assetization → optional extension
- Runtime内Overview/Review/Test → Runtime Manifest外へ分離
- 新checkpoint / 新P/J/M / Project Graph → 導入しない

残したContractはAuthority境界が異なり、単純統合すると責任衝突または再開情報消失が起きるためload-bearingと判定した。

## Cross-lens統合

最重要interactionは次の通り。

1. Human-LastはSafety/Authority/Risk/Budgetより下位。
2. Recoveryの自由度はEvidence ContractとAuthority Matrixで制限する。
3. Durable recordがなければOperation/Effect/Blockerの分離は再開時に崩れる。
4. Trust boundaryがなければResearch/Capability拡張がControl injection面を増やす。
5. BudgetがなければNo Progress回避がstrategy churnへ化ける。
6. Intent Fidelityがなければ全段階が正しくてもwrong goalをcloseできる。

## 最終判定

v0.2の形は、**小さいPolicy Kernelの外側に、交換可能なOperational Planeを置く**構成として妥当。

次の判定対象は設計の追加ではなく、Fault-injected Sandbox Runtimeで本当に契約通り戻ってこられるかである。
