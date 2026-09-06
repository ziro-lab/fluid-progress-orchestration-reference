# EFFECT_RECOVERY_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

外部世界を変更するEffectを、重複、応答喪失、rollback、補償失敗に耐える形で管理する。


Machine-authoritative Recordは `../schemas/fpo_records.schema.json` に従う。

### Effect class

- `read_only` — 外部変更なし
- `idempotent` — 同一intentの反復が安全に照合可能
- `compensatable` — 明示した補償で意味上戻せる
- `pivot` — 以後はforward recoveryを基本とするcommit point
- `irreversible` — 補償不能。事前Human gateと被害限定が必要

### state

- `intended`
- `started`
- `confirmed`
- `failed`
- `unknown`
- `compensating`
- `compensated`
- `compensation_failed`
- `forward_recovery_required`

### 実行前

Effect intent、logical intent、target / before revision、Effect class、Approval、precondition、idempotency / reconcile method、compensation / forward recovery planをcommitする。

外部操作直前にWork Control、Approval、target revision、Budget、Authorityを再確認する。

### Unknown outcome

開始記録後にresponseを失った場合、再実行せず外部世界をreconcileする。
`unknown`を放置したままcheckpointを進めない。

### Retry gate

同じlogical Effect intentを再実行してよいのは、次をすべて満たす場合だけである。

- stateが`intended`、または`failed / compensated`で再試行がDesign上許可されている
- `unknown / started / compensating / compensation_failed / forward_recovery_required`ではない
- `confirmed`済みEffectを重複実行しない
- idempotency / reconcile結果、current precondition、Approval、Budgetが有効

### Compensation / forward recovery

compensatable Effectが不要・有害になった場合、dependencyの逆順等、設計したorderでP3が補償を実行する。

pivot / irreversible後は、嘘のrollbackをせずforward recoveryまたはterminal safety dispositionを選ぶ。

compensation failureは新しいActive Blockerを作り、成功したふりをしない。

### Authority

P2がEffect recoveryを設計し、P3が実行・adoptし、P5が診断して正しいstageへrouteする。
P5やCapabilityが独断で補償Effectを実行しない。

### Closure

successful close時に`unknown`、`compensating`、`compensation_failed`、`forward_recovery_required`を残さない。
非成功terminalでも、残存Effectと外部世界の状態をfinal reportへ明示し、archive前のobligationを持たせる。
