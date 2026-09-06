# WORK_CONTROL_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

Achievement checkpointとは別に、workの活動・待ち・取消・有限終端、User control、Approval、Autonomy Budgetを管理する。


Machine-authoritative Recordは `../schemas/fpo_records.schema.json` に従う。

### Normative records

- `work_control` — current lifecycle projectionと、最新Budgetのadopted cache
- `control_event` — pause / resume / cancel / amendment / Approval / external condition
- `approval` — scope・revision・期限・revocationを持つAuthority grant
- `resource_budget` — immutableなBudget計測・更新Record
- `terminal_settlement` — completed / non-success terminalの最終状態と残存義務

`resource_budget`をBudgetのimmutable sourceとする。`work_control.autonomy_budget`はcurrent adopted projectionであり、`current_projection.budget_ref`が指す最新Recordと一致しなければならない。二重Authorityではなく、Record→projectionの関係とする。

### lifecycle state

```text
active
  ├─> suspended ──> active
  ├─> canceling ──> terminated
  └─> terminated
terminated ──> archived
```

- `active` — J1の通常dispatchが可能
- `suspended` — resume condition待ち。通常dispatch禁止
- `canceling` — 新規Operation / Effect禁止。既存Operationへcancelを伝播し、Effectをreconcile
- `terminated` — finite terminal。J1へ戻さない
- `archived` — retention / redaction処理済みの保管状態

terminal disposition:

- `completed`
- `canceled`
- `aborted`
- `unsatisfiable`
- `out_of_budget`
- `safety_stop`
- `out_of_scope`

`completed`だけが `checkpoint = closed` と対応する。

### Authority

- Userはpause / resume / cancel / amendment / approval grant・revokeを発行できる。
- RuntimeはBudget・Safety・schema・leaseに基づきsuspend / cancelingを開始できる。
- P5/M07は非成功terminalをrecommendできるが、Work Control Authorityが証拠・Policy・Approvalを検証して更新する。
- CapabilityはWork lifecycleを変更できない。

### Pause / resume

`suspended`にはreason、resume_condition、owner、expiry/default actionを必須とする。
条件成立・有効な入力・承認・外部eventが到着したときだけ`active`へ戻す。
単なる時間経過で推測再開しない。

### Cancel

cancel request受理後:

1. 新規Operation / Effectを禁止
2. cancel可能なactive Operationへ伝播
3. cancel不能・unknown Operationをreconcile
4. started Effectの状態と補償義務を確定
5. terminal reportをcommit
6. `terminated / canceled`へ移行

CancelはAchievementを`closed`にしない。
非成功終端も`record_type = terminal_settlement`へ最終状態、残存Effect、未完obligation、handoffを保存する。

### Amendment / rebase

User intent変更は上書きではなくevent化する。
Workをsuspendし、stale Operation / Approval / Evidenceを識別し、Active Blockerを作る。
P5→P1/P2/P3のAuthority経路でrebaseし、整合後にresumeする。

### Approval lifecycle

Approvalはapproval_id、grantor、scope、target / revision、allowed action / Effect class、conditions、valid_from、expires_at、revocation statusを持つ。

- scope外へ流用しない
- expiry / revocation後は実行直前gateで拒否
- Approval取得前にEffectを開始しない
- 古いdesign / targetへのApprovalを新revisionへ自動移行しない

### Risk Tier / v0.2 autonomy boundary

複数条件に該当する場合は最も高いTierを採用する。

- `T0` — read-only、外部Effectなし、公開または低機密data、決定論的に観測可能。通常は自律実行可。
- `T1` — localかつbounded・可逆な変更。外部公開、金銭、重要credential、物理Effectなし。Budgetとstandard sandbox内で自律実行可。
- `T2` — boundedな外部Effect、confidential data、moderate impactを含み得る。明示scope、least privilege、Approval、reconcile / compensation、強化Evidenceが揃う範囲だけ自律実行可。
- `T3` — 規制・医療・法務・重大金融、重大な不可逆公開/削除、物理危害、広範な権限、その他high-impact。FPO v0.2の自律P3実行範囲外。Research / Design / evidence preparationまではPolicyで許可できるが、専用domain controlとHuman Authorityへ早期handoffする。

Risk TierはCapabilityの強さで引き下げない。Risk条件の材料的変更はApproval・Definition・Designを再評価する。

### Autonomy Budget

Budgetは少なくとも次を必要な範囲で持つ。

- attempt count / strategy family count
- wall-clock / deadline
- token / monetary cost
- Tool / Research / Capability call count
- external Effect count
- context budget

usageはRuntimeが計測し、P5/M05は残量を前提にstrategyを選ぶ。
soft limitではsuspend / review、hard limitではPolicyに従い`out_of_budget`または明示Approval待ちとする。
Budget overrideはscope・増分・expiryを持つApprovalとして扱う。

### Finite termination

実現不能、Capability欠如、矛盾要件、Safety、Budget枯渇を永久Suspendにしない。
追加入力で解ける合理的なresume conditionがなければ、根拠と最終状態を残してterminal dispositionへ移る。
