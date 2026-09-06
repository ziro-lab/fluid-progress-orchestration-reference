---
doc_type: FPO.AUTHORITY_MATRIX
schema_version: 0.2
authority_owners:
  routing: J1
  definition: P1
  design: P2
  validation_method: P2
  target_mutation: P3
  execution_adoption: P3
  criteria_verdict: P4
  evidence_adoption: P4
  acceptance: P4
  predefined_validation_route: P4
  blocker_case: P5
  recovery_rollback_adoption: P5
  successful_closure: P6
  work_control_projection: runtime
  operation_lifecycle: runtime
  effect_lifecycle_projection: runtime
  durable_commit: runtime
---

# AUTHORITY_MATRIX
## FPO v0.2 — Normative Authority Source

### 目的

同じ判断を複数のJ/P/M/Capabilityが所有しないように、採用・変更・停止の最終Authorityを一意にする。

| 対象 | 最終Authority | 提案・材料提供 | 禁止 |
|---|---|---|---|
| source request / amendmentの発生 | User / trusted Work Control event | Capabilityは観測のみ | Task文書が暗黙変更しない |
| definition / requirement coverage / design discretion | P1 | Research / fidelity reviewer / P5 | Reviewerが直接採用しない |
| design / Validation method / Execution Plan | P2 | J2、M群、Research、P5 findings | P3/P4/P5/Capabilityが直接変更しない |
| Target / Artifact / compensation / forward recoveryの実行 | P3 | P2 design、P5 diagnosis、Capability Return | P5やCapabilityがTargetを直接変更しない |
| criteria verdict / Evidence adoption / Acceptance / predefined Validation failure route | P4 | Validator / Evidence producer / P2 Validation method | Worker self-accept禁止。Validation method designはP2。事前定義外のrollbackは禁止 |
| Blocker Set、diagnosis、diagnostic recovery rollbackの採用 | P5 | J3、M07、Research、Capability | P5はcheckpointを前進させない。P4の事前定義routeを横取りしない |
| successful closure / terminal settlement(completed) | P6 | P4 Acceptance、runtime preflight | 資産化をclosure前提にしない |
| 次P段階のrouting | J1 | なし | 原因判断・作業実行をしない |
| P2で必要なModule / Capability class | J2 | P2からの必要性 | 設計しない |
| P5で必要なModule / Capability class | J3 | Blocker facts | 継続・Human・terminalを決めない |
| 継続 / 切替 / 待ち / Human / terminal recommendation Policy | M07 | J3分類、Budget、Risk | Work Controlを直接更新しない |
| Work lifecycle / pause / cancel / non-success terminal disposition | Work Control Authority | User event、P5/M07 recommendation、runtime budget/safety | Capabilityが変更しない |
| Delegated Operation lifecycle | Runtime Operation Authority | Provider update | Provider stateをcheckpointに変換しない |
| Effect lifecycle / reconcile record | Runtime Effect Authority + P3 adoption | Provider / external observation | unknown outcomeを成功扱いしない |
| Evidence recordの生成 | Evidence producer | Tool / Agent / runtime | Acceptanceを変更しない |
| Evidenceの採用・contradiction解消 | P4（diagnostic用途はP5） | producer / verifier | producer自己採用だけで閉じない |
| schema / commit / projection / manifest validation | Runtime | なし | Task Contextから規則を補完しない |

### Mutation invariant

- P1だけがdefinitionを採用・変更する。
- P2だけがdesign / Validation method / Execution Planを採用・変更する。
- P3だけが通常Target / Artifact / Effectを変更する。
- P4だけがAcceptanceを成立させ、P2が事前定義したValidation failure routeを決定論的に適用する。
- P5だけがBlocker Setを閉じ、診断を伴うrecovery rollbackを採用する。
- P6だけがsuccessful `closed`を成立させる。

### Adoption invariant

Capability、Researcher、Validator、Runtime観測は、事実・候補・成果を返す。
それらをControl stateへ採用するのは上表のFPO Authorityである。

### Emergency invariant

RuntimeはSafety、cancel、schema破損、Authority失効に対してdispatchを停止できる。ただし停止をdefinition / design / Acceptanceの変更として扱わない。
