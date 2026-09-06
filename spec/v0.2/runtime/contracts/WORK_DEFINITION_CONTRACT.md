# WORK_DEFINITION_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

曖昧なsource requestから、原意を追跡できるdefinitionを作り、内部的には正しいがユーザー意図と異なる「仕様ロンダリング」を防ぐ。

### Normative records

Machine schemaは `../schemas/fpo_records.schema.json` の次を正とする。

- `source_request` — immutable original request / trusted amendment source
- `work_admission` — finite boundary、observability、Risk、Capability feasibility
- `work_definition` — P1が採用したDefinition
- `control_event` / `ledger_event` — amendment / rebase / user-control event

全recordはimmutableとし、変更は新revisionで行う。

### source request

- 原文または信頼済み構造化入力を改変せず保持する。
- clause / attachment / constraintをstable source item IDへ分ける。
- User amendmentは旧requestを上書きせず、amendment eventとして連結する。
- 外部WebやCapability提案をUser requestへ昇格させない。

### definitionの必須意味

- objective
- must conditions / wish conditions
- out-of-scope
- delegated design discretion
- assumption register
- decision priorities / tie-break / unacceptable trade-offs
- Risk Tier / required human gates
- source coverage matrix
- rejected interpretationsと理由
- unresolved items
- fidelity review requirement / result / P1 adoption

### Coverage rule

source itemは必ず次のいずれかへdispositionする。

- must condition
- wish condition
- design discretion
- out-of-scope（明示理由付き）
- unresolved blocker
- superseded by trusted amendment

未分類source itemを残したまま`defined`にしない。

### Assumption rule

各assumptionはbasis、impact、reversibility、validation route、statusを持つ。

- 低影響かつ可逆でAcceptanceを変えない → 設計裁量へ委譲可
- Acceptance、scope、Risk、不可逆性へ影響 → P1で解消またはBlocker
- 外部事実で確認可能 → Research / observation
- 本人固有Preference / Authority → required Human gate

### Decision Policy

優先順位は少なくとも、Safety、must condition、Authority、correctness、reversibility、cost/time、wish conditionの関係を明示する。
一般規則を固定順として押し付けず、work固有のtrade-offを記録する。

### Risk Tier

- `T0` — read-only、局所、外部永続Effectなし。通常は自律可。
- `T1` — boundedかつ可逆・照合可能なdigital write。明示scopeとBudget内で自律可。
- `T2` — 材料的な外部変更、費用、公開、または補償可能だが影響の大きいEffect。事前Approval・独立review・回復設計を要求する。
- `T3` — 規制、高stakes、物理不可逆、重大な権利・安全・資産判断。v0.2の自律admission対象外。

Risk TierはCapability能力ではなくwork/effectの許容境界である。Capabilityの`risk_ceiling`がwork tier未満なら採用しない。

### Fidelity review

次のいずれかでは独立reviewを要求する。

- 高曖昧で複数解釈がmust / scopeへ影響
- `T2`以上のRisk
- 大きな不可逆Effect
- source item数が多くcoverage脱落リスクが高い

Reviewerはsource→definitionの欠落・歪みを返すだけで、definitionを変更しない。P1が採否と根拠をcommitする。

### Amendment / rebase

trusted amendment到着時はWork Controlが通常dispatchを止め、amendment eventとBlockerを作る。
P5が影響範囲を整理し、必要なcheckpointまで戻し、P1が新definition revisionを採用する。
遅延Returnや古いApprovalを新revisionへ自動採用しない。
