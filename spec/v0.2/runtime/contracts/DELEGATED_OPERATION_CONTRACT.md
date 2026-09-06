# DELEGATED_OPERATION_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

外部Agent / Tool / Harnessへ委譲した一回以上の長時間処理を、crash、delay、cancel、重複、成否不明に耐えるOperation lifecycleとして管理する。


Machine-authoritative Recordは `../schemas/fpo_records.schema.json` に従う。

### Identity

- `logical_intent_id` — 同じ意味上の仕事。retry間で維持
- `dispatch_id` — instruction / input / constraint revision
- `attempt_id` — 実送信ごとに一意
- `remote_operation_id` — provider側識別子。取得可能な場合
- `plan_unit_id` / `owner_stage`
- Capability identity / revision / binding

instructionやtargetが材料的に変わった場合、同じdispatchとして偽装しない。意味上のGoalが同じ場合だけlogical intentを維持する。

### Dispatch Packet

送信内容は`message_type = dispatch_packet`のschema-valid immutable messageとして保存する。少なくとも次を含む。

- dispatch / work / logical intent / attempt / Plan Unit identity
- owner stage、Capability identity / revision / binding
- current Definition / Plan / Target / Policy revision
- objective、input refs、constraint refs
- allowed Effect refs、Approval refs
- required Artifact contract、required Evidence claim
- Return schema、deadline

Operation `prepared` recordは`dispatch_payload_ref / dispatch_payload_sha256`を保持し、Packetと同じsemantic commitへ採用してから送信する。送信後のPacketを上書きしない。Packetの材料的変更は新しい`dispatch_id`とし、再送だけなら新しい`attempt_id`を使う。

CapabilityはPacketをTask Contractとして受け取るが、PacketはWORK_STATE・Work Control・Acceptanceを変更するControl commandではない。

### Operation state

```text
prepared -> submitted
submitted -> running | waiting_input | waiting_authorization | succeeded | failed | rejected | timed_out | canceled
running <-> waiting_input
running <-> waiting_authorization
running/waiting_* -> succeeded | failed | rejected | timed_out | canceled
nonterminal + lease loss/response ambiguity -> unknown
unknown -> running | waiting_input | waiting_authorization | succeeded | failed | rejected | timed_out | canceled  （reconcile後）
```

`unknown`を成功・失敗のどちらにも推測しない。外部照合またはprovider queryでreconcileする。

### Lease / heartbeat / deadline

Capability profileに応じてheartbeat、lease_expires_at、deadline、poll / stream方法を記録する。
lease失効だけで再送せず、remote statusとEffectを照合する。

### Cancel

cancel request、request time、provider ack、terminal statusを区別する。
Providerがcancel非対応なら、結果をadoptしないことと、Effectをreconcileすることを別に扱う。

### Return / update

Returnは専用Untrusted Inboxへimmutable・content-digested・schema-valid dataとして保存する。Operation recordは`dispatch_payload_ref / dispatch_payload_sha256`と`return_ref / return_sha256`を保持し、送受信した正確な内容を固定する。
provider sequence / attempt_id / dispatch_id / target revisionを照合し、duplicateはidempotently無視、out-of-order / stale updateはadoptしない。

partial artifact / Evidence / Effect refは記録できるが、terminal successやFPO checkpointを意味しない。

### Adoption

Operation `succeeded`とP3/P5の`adoption_status`を分ける。

- `pending`
- `adopted`
- `rejected`
- `superseded`

owner stageが現在のdefinition / design / target / policy revisionへ照合してadoptする。

### Retry

retryは新attempt_idを発行し、logical_intent_idとEffect intentを維持して重複を照合する。
成否不明、cancel未確定、Effect unknownの間は自動retryしない。

### Authority

CapabilityはOperation state updateを返せるが、WORK_STATE、Work Control、Blocker、Acceptanceを変更できない。
