# FPO v0.2 Architecture Decisions

## ADR-001 — 6 checkpointを維持する

Achievementの成立地点は `none / defined / designed / executed / accepted / closed` に限定する。
Operation待機、取消、失敗、No Progressをcheckpointへ混ぜない。

## ADR-002 — Operational Planeを外部Recordとして持つ

Work Control、Operation、Blocker、Evidence、Effect、Trust/Durabilityを分離する。
外へ出した複雑さを「存在しない」ことにせず、Contractで閉じる。

## ADR-003 — J1の前にRuntime Control Gateを置く

Pause、Cancel、Terminal、Budget、ApprovalはJ1の仕事ではない。
Runtimeが機械的Gateを通したactive workだけをJ1へ渡す。

## ADR-004 — P5はProgress Recovery ownerであり万能Executorではない

P5はBlocker、Progress、rollbackを所有する。
Definition/Design/Target/Acceptanceの変更は各ownerへ返す。

## ADR-005 — Authority Matrixを規範化する

J3は分類と必要能力、M07は継続Policy、P5はBlocker/rollback、P4はcriteria verdictと事前定義failure routeを持つ。

## ADR-006 — Markdownをcanonical record surfaceにする

YAML front matterをcontrol payload、本文を説明・raw materialとする。
commit ledgerとprojectionでcrash/replayを扱う。

## ADR-007 — Runtime ContextをManifestで限定する

Overview、Validation、Review、Template、ExtensionをRuntime Control Contextへ入れない。

## ADR-008 — ClosureとAssetizationを分離する

P6はsettlement/handoff/closeだけを行う。
Assetizationはoff-by-default extensionまたは別work。

## ADR-009 — Human-Lastは有限Budget内のPolicy

Humanを呼ばない時間を無限化しない。
Safety、Authority、Risk、Budgetが先に効く。

## ADR-010 — v0.2はsingle-work boundaryを守る

一つのglobal checkpointが意味を持たないGoalはadmitしない。
Multi-workはRuntime実証後の別設計課題とする。

## ADR-011 — Validation failure routeとRecovery rollbackを分ける

P4はP2が事前定義した決定論的failure routeだけを適用する。原因診断を伴うrollbackはP5が所有する。

## ADR-012 — Projection aliasとimmutable Recordを分ける

安定名WORK_STATE / WORK_CONTROL / WORK_INDEXは再構築可能なaliasであり、正本はschema-valid immutable snapshotとCommit chainである。

## ADR-013 — Dispatch/Return本文をOperationへdigest bindingする

Operation IDだけでは再開時に「何を送ったか」を確定できない。trusted outbound `dispatch_packet`とuntrusted `capability_return`を別messageとして保存し、`delegated_operation`が正確なref/hashを固定する。Packet/ReturnはControl Stateではない。

## ADR-014 — Unit/Budgetはimmutable source、projectionはcache

`plan_unit_state`と`resource_budget`を履歴・replayのsource Recordとする。`current_projection.unit_states`と`work_control.autonomy_budget`は再開用cacheであり、source Recordと不一致ならfail closedして再構築する。Runtime profileごとの二択を廃止する。

