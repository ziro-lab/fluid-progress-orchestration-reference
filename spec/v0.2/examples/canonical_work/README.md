# Canonical Interrupted Work Example

`W-EXAMPLE`は正常完了例ではなく、**Dispatch後にprovider応答が失われ、OperationとEffectがunknown、Evidenceもdiagnostic止まり**の中断状態を表す。

この例で確認できるもの:

- source requestからDefinitionへのcoverage
- immutable Budget / Plan Unit source Recordとprojection cacheの一致
- exact outbound `dispatch_packet`と`delegated_operation`のdigest binding
- untrusted `capability_return`とowner adoptionの分離
- multiple external recordsを一つのsemantic Commitへ採用
- unknown Operation / Effectを成功・失敗に推測しない
- Active Blocker、Progress Claim、UNKNOWN criteria verdict
- current projectionの再構築可能性

`commits/COM-0001.md`は`global/`、`records/`、`packets/`、`projections/`、`observations/`の採用入力をdigestで固定する。`inbox/untrusted/`は採用前材料なのでCommitへ直接含めず、Operation Recordが正確なReturn digestを保持する。
