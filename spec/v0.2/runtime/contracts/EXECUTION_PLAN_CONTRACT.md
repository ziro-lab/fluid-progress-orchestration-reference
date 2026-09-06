# EXECUTION_PLAN_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

一つのfinite workを、Project Graphを導入せず、crash後に部分再開できるstable Plan Unitへ分解する。


Machine-authoritative Recordは `../schemas/fpo_records.schema.json` に従う。

### Normative records

- `validation_method` — P2が採用する検査方法
- `execution_plan` — stable Plan Unit設計
- `plan_unit_state` — immutableなUnit state transition/source Record
- `artifact_manifest` — P3が採用・保留・棄却したArtifact identity / revision

`current_projection.unit_state_refs`はcurrentな`plan_unit_state` Recordを指し、`unit_states`は再開用cacheとしてその内容と一致しなければならない。二重Authorityではなく、Record→projectionの関係とする。

### Plan Unitの必須意味

- stable `unit_id`
- objective / owner stage
- dependencies / preconditions
- required input / target revision
- Capability class / delegated operation intent
- expected artifact / claim / Evidence / Effect
- validation hook
- retry / stop / switch条件
- known failure routes
- optional compensation / forward recovery hook

Plan designと実行stateを分ける。Plan recordはP2 Authority、unit execution projectionはP3 / Runtimeの採用結果である。

### Unit state

- `pending`
- `ready`
- `running`
- `blocked`
- `succeeded`
- `failed`
- `skipped`
- `superseded`

Unit `succeeded`は、必要Operation / Effect / ArtifactがP3にadoptされ、validation hook用のEvidenceが記録可能な状態を表す。

### Dependency / resume

依存Unitのadopted resultとrevisionをpreconditionで確認する。
crash後はcurrent projectionから`succeeded` unitを再利用し、未adopt / stale / invalidated unitだけを再開する。

Target / design / dependency変更は、影響するUnitだけをsupersedeする。影響範囲はM04で設計する。

### Known failure route

P2は予測可能な失敗について、観測条件とrouteを事前定義できる。

- retry current design → `designed`
- redesign required → `defined`
- redefinition required → `none`
- validation repeat → `executed`
- unknown / cause processing → Active Blocker

P4は観測結果がroute条件へ明確に一致する場合だけ直接適用する。

### Scope boundary

v0.2は逐次single-work Coreを維持する。Plan Unitは部分再開のためであり、parallel schedulerやmulti-work Project Graphを意味しない。
