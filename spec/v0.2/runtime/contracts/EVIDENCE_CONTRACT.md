# EVIDENCE_CONTRACT
## FPO v0.2 / contract 0.2
### 役割

Evidenceが「何を、どのrevision・method・環境・lineageから、どの範囲まで支えるか」を明示し、stale・相関・部分・矛盾によるfalse closeを防ぐ。


Machine-authoritative Recordは `../schemas/fpo_records.schema.json` に従う。

### Normative records

- `validation_method` — P2が採用したmethod identity / revision
- `evidence` — producer由来の観測とlineage
- `criteria_verdict` — P4がcurrent criterionへ採用したPASS / FAIL / UNKNOWN / NOT_APPLICABLE

Evidence recordとcriteria verdictを同一視しない。Evidence producerはVerdictやAcceptanceを所有しない。

### Evidenceの必須意味

- evidence_id
- claim_id / criterion_id
- method_id / method_revision
- object / target revision
- design / plan revision
- environment revision
- observed_at / freshness policy / expires_at
- producer / verifier / trust domain
- source lineage
- coverage
- independence basis
- status
- supersedes / contradiction refs
- artifact / raw observation refs

### status

- `proposed`
- `valid`
- `superseded`
- `contradicted`
- `retracted`

Evidence producerは`proposed`として提出し、P4または診断用途のP5がAuthority範囲で採用する。

### Freshness / invalidation

対象、design、environment、method、Capability revisionの材料的変更でEvidenceを再評価する。
依存対象が変わったEvidenceを自動的に現行へ流用しない。

### Coverage

criterion全体、部分、サンプル、負の反例等を区別する。
部分coverageを全体へ拡張するには、外部規則または追加Evidenceが必要。

### Independence

別Capabilityというだけで独立としない。

- model/provider
- raw source
- execution path
- evaluator prompt / code
- environment
- human / machine trust domain

のlineage重複を確認し、材料的に独立な根拠を記録する。
独立性不要のcriterionでは過剰な二重確認を要求しない。

### Contradiction

同一claimにcurrentかつvalidな矛盾Evidenceがある場合、P4はAcceptanceしない。
contradiction解消Evidence、適用範囲分離、retraction / supersede決定をcommitする。

### Validation method adoption

新method revisionは次を持つ。

- covered claims
- change reason
- expected strength
- equivalence / strengthening Evidence
- independent support requirement

P2はmethod自身の結果だけでmethod adoptionを正当化しない。
P4はP2がadoptしたcurrent methodだけをAcceptanceへ使用し、adopt前のmethod EvidenceをAcceptanceへ使用しない。

### Acceptance algorithm

P4はcurrent revisionへ対応するvalid Evidence setを構成し、coverage、freshness、contradiction、independence、method adoptionを確認する。External ValidatorのPASSはEvidenceの一つであり、Acceptance decisionそのものではない。
