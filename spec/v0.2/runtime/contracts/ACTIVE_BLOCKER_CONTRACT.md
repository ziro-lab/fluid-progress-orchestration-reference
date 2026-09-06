# ACTIVE_BLOCKER_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

通常Coreを止める問題を、複数件・依存・待ち・部分解消を失わずに扱い、P5が正しいAuthorityへ戻せるようにする。


Machine-authoritative Recordは `../schemas/fpo_records.schema.json` に従う。

### Normative records

- `blocker_set` — WORK_STATEから参照するactive set projection
- `blocker` — 個別case、status、依存、rollback recommendation
- `progress_claim` — P5が採用するnet material Progress評価

### Blocker Set

`WORK_STATE.interrupt_ref` はBlocker Set projectionを参照する。
Setは少なくとも次を持つ。

- set_id / state revision
- active blocker refs
- blocking count
- waiting count
- global / local scope summary
- last P5 decision ref

active blocking entryがゼロになるまでinterruptを解除しない。

### Blocker status

- `open`
- `investigating`
- `waiting`
- `resolved`
- `superseded`

waitingにはresume condition、owner、expiry/default actionを必須とする。
Work Controlを`suspended`へ移すのは、(a) global Safety / Authority gateである場合、または (b) 全blocking Blockerがwaitingで、現在実行可能なRecovery pathが残っていない場合だけとする。
他の`open / investigating` Blockerを処理できる間はworkをactiveに保ち、P5がそれらを進める。

### Blockerの必須意味

- kind / source stage / scope / affected revision
- symptom
- candidate causes
- earliest unrepaired error
- contributing factors
- detection gap
- dependencies
- attempt refs / strategy family
- Progress claims
- required Evidence / Capability / Approval
- next normal Authority
- rollback recommendation
- resolution Evidence / close condition
- optional terminal recommendation

### Error lifecycle

最終症状とroot causeを同一視しない。

- symptom — 現在観測された失敗
- earliest unrepaired error — 因果鎖で最初に残っている誤り
- root cause — 修復しなければ再発する中心原因
- contributing factor — 発生・増幅に寄与
- detection gap — 早期に見つけられなかった理由

原因不明はstatusであり、根拠なしのroot causeを作らない。

### Progress claim

Progress claimには次を含める。

- 対象Blocker / claim
- before / after uncertaintyまたは成立範囲
- newly adopted Evidence / finding / route
- invalidated / contradicted Evidence
- cost / risk / debt / scope divergence
- strategy familyと既試行との差
- net materiality判断と根拠

単に新しいファイル、検索、Capability、名称違いの戦略を得ただけではProgressにしない。

### Resolution

個別Blockerをresolvedにするには、resolution Evidenceと現在revisionへの適用可能性を確認する。
依存Blockerが残る場合、Setを閉じない。

P5は解決そのものがP1/P2/P3/P4 Authorityを要する場合、そのAuthorityで扱える状態へ変換した時点でBlockerを解消できる。まだ修正されていないTargetを「修正済み」と記録しない。

### Scope

`global` / `plan_unit:<id>`を区別する。v0.2のCoreは逐次であるため、local blocking entryも安全側にCore全体を停止する。将来の並列継続を暗黙実装しない。
