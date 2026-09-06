# WORK_STATE
## FPO v0.2 / Achievement Projection schema 0.2

### Machine representation

Machine-authoritative snapshotは `../schemas/fpo_records.schema.json` の `record_type = work_state` に従う。

```yaml
schema_name: fpo.record
schema_version: "0.2"
record_type: work_state
# common immutable record envelopeは省略
payload:
  checkpoint: none
  interrupt_ref: null
```

work rootの安定名 `WORK_STATE.md` を使う場合、それはlatest committed `work_state` snapshotの再構築可能なalias / cacheであり、正本はimmutable Recordとvalid Commitである。
`work_state` record自身の`record_revision / base_state_revision`はimmutable envelopeに従う。現在採用中の`state_revision / current_commit_id`は`record_type = current_projection`から取得し、WORK_STATE aliasへ二重Authorityを持たせない。

### 意味

`checkpoint` は世界の履歴ではなく、**現在の外部世界と採用済み根拠に対して、その地点までの成立を主張できること**を表すAchievement stateである。

許可値は次の6個だけ。

- `none`
- `defined`
- `designed`
- `executed`
- `accepted`
- `closed`

新しいAchievement checkpointを、外部Operation・待機・失敗・取消・No Progressの表現目的で追加しない。
それらは責任別Operational Planeで扱う。

### checkpoint規律

- 前進前に、所有P段階が成立根拠をvalid commitへ含める。
- 入力、前提、環境、対象、Design、Verification methodの変更を検出した所有P段階またはP5は、現在も成立する最後の地点まで維持または後退させる。
- P4はP2が事前定義したValidation failure routeだけを決定論的に適用できる。診断を伴うrollbackはP5が採用する。
- 後退しても既存の外部Effectは巻き戻ったと仮定しない。
- `closed` は成功完了のAchievement終端だけを表す。取消・実現不能・予算切れ等はWork Control terminal dispositionで表す。

### Progress

Progressはcheckpointの単調前進ではない。
根拠ある後退、materialなEvidence増加、不確実性低下、原因限定、Effect整合回復などにより完遂可能性がnetで増すことを含む。

Strategy変更、Tool利用、Token消費、活動量だけをProgressとしない。

### interrupt_ref

`interrupt_ref` はActive Blocker Setへの参照である。

- `null`: 通常Routingを止めるopen / investigating / waiting Blockerがない
- non-null: `ACTIVE_BLOCKER_CONTRACT.md` に従うBlocker Setが存在する

Blockerは複数件を個別statusで保持する。一件解消だけで他のblocking Blockerを消さない。

### projection

work rootのprojection aliasがcommit ledgerと一致しない場合、J1へ渡さずvalid commitから再構築する。
