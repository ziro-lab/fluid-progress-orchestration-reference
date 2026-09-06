# EXTERNAL_STATE_LAYOUT
## FPO v0.2 Reference Layout

```text
/fpo-runtime/
  RUNTIME_ENTRY.md
  RUNTIME_MANIFEST.md
  core/
  contracts/
  schemas/

/work/W-0001/
  WORK_STATE.md                 # latest committed work_state alias/cache
  WORK_CONTROL.md               # latest committed work_control alias/cache
  WORK_INDEX.md                 # latest committed current_projection alias/cache

  commits/
    COM-0001.md                 # immutable semantic commit

  records/
    SRC-0001.md                 # source_request
    CTRL-0001.md                # control_event
    EVT-0001.md                 # ledger_event / audit event
    ADM-0001.md                 # work_admission
    DEF-0001.md                 # work_definition
    VM-0001.md                  # validation_method
    BUD-0001.md                 # immutable resource_budget measurement/source
    PLAN-0001.md                # execution_plan
    UNITSTATE-0001.md           # immutable plan_unit_state transition/source
    APR-0001.md                 # approval
    OP-0001.md                  # delegated_operation; binds exact Dispatch/Return digests
    EFF-0001.md                 # effect
    EVD-0001.md                 # evidence
    VER-0001.md                 # criteria_verdict
    BLKSET-0001.md              # blocker_set
    BLK-0001.md                 # blocker
    PRG-0001.md                 # progress_claim
    ART-0001.md                 # artifact_manifest
    SET-0001.md                 # terminal_settlement

  packets/
    DISP-0001.md                # trusted outbound fpo.dispatch_packet message

  inbox/
    untrusted/
      RETURN-raw-0001.md        # fpo.capability_return message; not adopted state
      WEB-raw-0001.md

  observations/
  staging/
  archive/
```

### Source of truth

- immutable Record + valid Commitが正本
- `WORK_STATE / WORK_CONTROL / WORK_INDEX`の安定名はcommitted snapshotのalias / cache
- `record_type = current_projection` が再開時のcurrent refsを持つ
- `plan_unit_state`と`resource_budget`はimmutable source Record
- `current_projection.unit_states`と`work_control.autonomy_budget`は再構築可能なadopted cache
- Context projectionは再読込用でありAuthorityを持たない
- trusted outbound Dispatch Packetは送信内容のTask Contractであり、Control Stateではない
- Untrusted Inboxは採用前の材料でありControl Stateではない

### 更新単位

同じsemantic decisionに属するRecord、outbound Packet、projection snapshotを一つのcommitへまとめる。

1. candidate Record / Packet / snapshotをstagingへ書き、schemaとdigestを検査
2. CommitをCASでpublish
3. stable aliasをlatest committed snapshotへ更新

Commit前のcrashはorphan、Commit後・alias更新前のcrashはledgerから再構築する。
複数MDを「同時に書けたように見える」ことへ依存しない。

### Projection/cache rule

- `current_projection.unit_state_refs`がcurrentな`plan_unit_state` Recordを指す
- `current_projection.unit_states`はそのcurrent stateのcacheであり、source Recordと一致する
- `current_projection.budget_ref`がcurrentな`resource_budget` Recordを指す
- `work_control.autonomy_budget`はそのBudgetのcurrent adopted cacheであり、source Recordと一致する
- 不一致はprojection driftとしてfail closedし、immutable RecordとCommit chainから再構築する

Schema-only terminal fixture等は`examples/schema_fixtures/`へ分離し、canonical workのCommitへ混ぜない。
