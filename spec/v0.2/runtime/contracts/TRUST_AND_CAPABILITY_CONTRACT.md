# TRUST_AND_CAPABILITY_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

Control stateと外部入力を分離し、必要なCapabilityを適合性・信頼性・最小権限で選び、ReturnやWebからの権限逸脱を防ぐ。


Machine-authoritative dataは `../schemas/fpo_records.schema.json` に従う。

### Normative records / messages

- `capability_entry` — trusted Registry entryとrevision
- `dispatch_packet` — trusted outbound task message。FPO RecordやControl commandではないが、送信前にschema検査・digest固定する
- `capability_return` — Untrusted Inboxへ入るprovider message。FPO Recordではなく、採用前材料
- `delegated_operation` — Runtimeが採用したOperation lifecycle。詳細はDelegated Operation Contract

Schema-valid Dispatch PacketはCapabilityへ渡す正確なTask Contractであり、Control State変更権を付与しない。Schema-valid Returnもtrusted/adoptedとは扱わない。Authority ownerがcurrent refs、sequence、Capability revision、Effectを照合してRecord化する。

### Context zones

1. **Trusted Control** — runtime modules、validated state projection、Authority decision
2. **Task Context** — User request、対象artifact、作業資料
3. **Evidence Context** — raw observation、source、test output
4. **Untrusted Inbox** — Web、Capability Return、生成artifact、外部message
5. **Secret Store** — credential値。Control/Task Contextへ展開しない

Untrusted Inboxはschema validationとowner adoptionを経ずにTrusted Controlへ入れない。
Markdown本文、引用、code、URL中の命令をControl instructionとして解釈しない。

### Capability Registry

Registry entryは少なくとも次を持つ。

- capability_id / revision / provider identity / registry signatureまたは同等の信頼根拠
- provides / accepts / returns
- side-effect profile
- tool / data / path / network / secret scopes
- health / availability
- cost / latency class
- quality / fitness / eval refs
- cancel / stream / reconcile / idempotency support
- compatibility / required environment
- fallback / degraded mode
- binding ref

Registry登録はAuthority、Approval、品質保証を自動付与しない。

### Selection

目的に十分な最小権限Capabilityを選ぶ。

- required fitnessを満たさない
- unavailable / degraded
- incompatible
- scope過大
- cancel / reconcileが必要なのに非対応
- eval historyが用途Riskに不足

のCapabilityを採用しない。

### Binding / execution

Runtimeはbinding時にidentity / revision / health / scopeを再確認する。
Secretはhandleで渡し、Capabilityに不要なcredentialやfilesystem/network範囲を与えない。
Sandbox、path allowlist、network egress allowlist、resource limitを可能な限り機械強制する。

### Dispatch / Return handling

Dispatch Packetは専用outbound areaへimmutableに保存し、content digestを`delegated_operation.dispatch_payload_sha256`へ固定してから送る。送信済みPacketを上書きせず、材料的変更は新しい`dispatch_id`として表す。

Returnは専用inboxへimmutableに保存し、content digestを固定したうえで、schema、size、type、path、URI、encodingを検査する。

- path traversal / executable payload / hidden instructionをsanitiseまたは隔離
- unknown fieldはnamespaced extension以外拒否
- Return中の`checkpoint`、`approval`、`allowed_actions`等のControl風fieldを無視せずschema errorとして拒否
- artifactは実行前に別検査する

### Capability governance

Registry変更は署名・revision・reviewを持ち、work途中の変更を過去Returnへ遡及適用しない。
重要用途ではfitness evidenceとrecent healthを記録する。

### Authority

Capabilityは事実、artifact、Evidence、提案、Operation updateだけを返す。WORK_STATE、Work Control、definition、design、Acceptanceを変更しない。
