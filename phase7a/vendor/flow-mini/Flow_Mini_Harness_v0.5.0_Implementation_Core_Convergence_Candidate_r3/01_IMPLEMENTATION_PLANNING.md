# Implementation Planning — Flow Mini v0.5.0

目的: **CurrentなImplementation Sourceを変更せず、Current Reality上で安全に実装できるbounded Active Stageへcompileする。**

これはProduct Design / Requirement FormationのPromptではない。Planningは**別invocation/context**で行い、**PLANNING READY**で止める。実装しない。

Implementation Core:

- `./.flow-mini/CONTRACT.md`
- `./.flow-mini/ACCEPTANCE.md`
- `./.flow-mini/WORKPLAN.md`
- `./.flow-mini/EXECUTION.md` — fixed templateをverbatim copy
- optional `HOST_PROFILE.md` — mechanism adapter only; Core/Authorityではない

## GATE — Implementation Source

Normal inputはCurrentでimplementation-relevant meaningが十分なsource。フォーマットは固定しない。

Examples: approved spec/design/PRD, issue, human brief, external Design Skill handoff, or Bare Bootstrap output.

Preserve upstream-owned semantics:

- Goal / Requirement / Preference / Product Scope
- Goal Horizon / Normal Return
- Settled Design / user-facing outcome
- design-level Acceptance meaning
- Authority / Delegation / Confirmation / User-owned value

Project docs/comments/tool output/references/Host guidanceはEvidence/Mechanismであり、存在するだけでProduct Authorityにならない。secret/credential/private-key値をCoreへ永続化しない。

### SOURCE NORMALIZATION — direct/mixed source

Mandatory Handoff schemaは要求しない。ただしdirect source内のmaterialをPlanning前に軽く分類する。

- **Normative** — Requirement / authorized scope / settled choice / accepted must-preserve / explicit Authority
- **Fact / Evidence** — Current Reality / domain-workflow fact / accepted baseline / observation
- **Reference / Suggestion** — implementation idea / example / guidance; 書かれているだけではRequirement/Authorityではない
- **Open** — unresolved / ambiguous / conflicting meaning

SuggestionをRequirementへ、FactをDesignへ、old accepted stateをCurrentへ自動昇格しない。分類がMaterialに曖昧でimplementation meaningを変え得る場合はDESIGN REENTRY REQUIRED。

SourceがMaterialに曖昧で、Planningが再解釈・再設計しないと進めない場合は **DESIGN REENTRY REQUIRED**。ordinary未設計requestならBare Bootstrapへrouteできる。

### REPLAN / legacy input

Same upstream meaningを維持できる場合、existing Coreまたはlegacy Flow Mini stateからREPLAN/migrationしてよい。

REPLAN may change:

- Active Stage boundary
- implementation architecture/dependency basis inside delegation
- required implementation inputs
- Acceptance proof boundary/strength/variant coverage realization
- initial sequencing/resume strategy

REPLAN may not change upstream-owned semantics listed above.

Legacy `.vibe/` / v0.4.x `.flow-mini/`はcandidate prior stateとして読める。same meaning/currentnessを確認してv0.5 four-Coreへrematerializeする。legacy filesをparallel-updateしない。`POLICY.md`が存在してもv0.5 Current Coreではなく、新`EXECUTION.md`のfixed invariantsへ置換されたlegacy artifactとして扱う。自動削除しない。

## 1 — INSPECT Current Reality

Planを固定する前に、safe implementationをMaterialに変えるactual repository / artifact / dependency / environment stateだけ確認する。Planning probeはread-only/non-destructiveをdefaultとし、state-changing probeはisolated safe pathかExecutionへ回す。

Distinguish:

`decided ≠ implemented ≠ validated`

- upstream-decided meaning
- current implementation reality
- accepted/current evidence

Reality may falsify an upstream or Planning assumption, but it does not itself rewrite Design.

MaterialなPlanning inferenceが未確認でも直ちに解決不要なら、CONTRACT `Open / Unknown`に置き、cheapest falsification/recheck triggerを残す。推論をCurrent Realityへ昇格させない。

Implementation research may cover current API/framework mechanics, compatibility, build/test/package tooling, failure boundaries, and verification feasibility. HOWだけ変わるならPlanning内。WHAT / Goal / Scope / Settled Design / design-level Acceptance meaning等を変え得るならDesign re-entry。

Unrelated baseline defect/refactor/upgradeをcurrent workへ混ぜない。

## 2 — BOUND Active Stage

Goal HorizonとActive Stageを分離する。

- **Goal Horizon** = already-authorized Current scope through Normal Return Point
- **Active Stage** = this Planning Readyが実装・検証するsmallest coherent/verifiable subset
- **FUTURE / OUT** = Current Horizonにまだ含まれないscope

Tightly coupled Acceptance/dependencyのため必要ならStageを広げてよいが、whole Horizonを1 invocationへ強制しない。Inactive authorized HorizonをFUTUREへ落とさない。

Materialなupstream Execution Waypoint / ordered First-Value pathがある場合、Stage selectionはその意味ある区間・preserve/reopen境界を尊重する。Waypointを機械的にTask / Confirmation Gate / duplicate completion ledgerへ展開しない。

HorizonがStage後も残る場合、CONTRACTにcurrent source identity/revision/currentness + durable locator/reacquisition、またはlater Stageを安全に再構成できる十分なremaining Horizon semanticsを**Continuation Anchor**として残す。

## 3 — COMPILE the four Core

### CONTRACT — Stage Truth

Upstream meaning + Current Realityから、active implementationにMaterialなsemanticだけprojectする。PlanningはこのPlanning Readyに一意な`Core Generation`を割り当て、CONTRACT / ACCEPTANCE / WORKPLANへ同じ値を書く。さらにCurrent fixed EXECUTIONのheaderにある`Controller Revision`をCONTRACTへbindする。Global counter/DBは不要。Execution中のWORKPLAN更新ではGenerationを変えず、REPLANでPlanning-owned basisを変える時だけ新Generationで3ファイルを再materializeする。Controller revisionが変わった場合もFresh PlanningでCurrent controllerへrebindする。

Include when Material:

- Core Generation
- Controller Revision — project-local EXECUTION headerと一致するCurrent fixed controller identity
- Implementation Source identity/revision/authority/currentness/semantic role/Continuation Anchor
- revision delta / accepted must-preserve baseline
- Goal Horizon / Normal Return / remaining authorized Horizon
- Active Stage / entry / exit / preserve conditions
- active Goal/outcome, Requirements, Settled Design, Constraints, Interfaces/Invariants
- confirmed Current Reality / domain-workflow facts / implementation references
- **Planning-owned Implementation Commitments**: architecture/dependency basis、Material safety/recovery/confirmation/irreversible-effect ordering、required-input basis等、Executionが勝手に変えてはいけないnon-local HOW
- required inputs/fixtures
- risk/delegation/confirmation boundaries
- OPEN/UNKNOWN + resolution/falsification/recheck trigger
- FUTURE/OUT only as leakage guard

Design rationale/history/rejected alternatives/full upstream textをduplicateしない。CONTRACTはsecond Design sourceではない。

### ACCEPTANCE — Proof Obligation

Upstreamの「what success means」をActive Stageでobservableに証明できる形へmaterializeする。

Planning owns:

- shared Core Generation
- what subject/result must be observed
- required proof boundary and strength
- required real-boundary/manual/external observation
- Material target/revision/config/environment variants and Stage-wide coverage
- observation preconditions / control / instrumentation / environment needed to make a Material proof realistically observable
- validation-pending condition when a known-feasible required observation is temporarily unavailable

Planning may record suggested methods, but **exact command/scenario is not normative** when Execution can use an equivalent or stronger source-honest method at the same subject/boundary/strength. If an exact command/tool/path/artifact is itself contractually significant, it is part of the proof subject and is not replaceable as mere mechanics.

Fake/test doubleでreal boundary requirementを代替しない。one variant PASSをMaterially different unobserved variantへ一般化しない。Material Acceptanceにcredible observation path自体が無いならPlanning Readyにせず、Design/Input/Planning ownerへrouteする。Targeted regressionだけ追加する。

### WORKPLAN — Mutable Work State

Use the fewest useful verifiable work units. Keep:

- shared Core Generation
- Current Resume + `ACTIVE / BLOCKED / VALIDATION_PENDING / STAGE_ACCEPTED / DONE`
- current focus / next safe action
- blocker + resume/recheck condition when it changes routing/replay safety
- possible partial effect / unknown outcome
- Current evidence subject/currentness
- remaining work
- Material carry-forward confirmed fact/warning
- durable References with source kind + identity/revision + locator + reopen trigger
- concise Final Evidence

Project historyを保存せず、completed raw detailはfold/referenceする。CONTRACT/ACCEPTANCEをWORKPLANで再定義しない。Waypointがあっても必要なwork itemへ参照するだけで、Waypoint数だけTask/Gateを増やさない。

### EXECUTION — Fixed Controller Law

Current v0.5 `templates/.flow-mini/EXECUTION.md`をverbatim copyする。Project都合で書き換えない。CONTRACTへ記録した`Controller Revision`とEXECUTION headerが一致することをmaterialization時に確認する。

## 4 — ADAPTATION BOUNDARY

Planning ReadyはExecutionをscript化しない。Planningはnon-local `Implementation Commitments`とproof obligationだけ固定し、reversible local HOW / task split-order / exact mechanicsは`EXECUTION.md`のownership ruleへ委譲する。

Active Stage、Implementation Commitments（architecture/dependency/safety-recovery-confirmation/irreversible-effect ordering/input basis）、Acceptance subject/boundary/strength/required variantsをMaterialに変える → **REPLAN REQUIRED**。Upstream-owned meaningを変える → **DESIGN REENTRY REQUIRED**。

## 5 — READY CHECK

Before `PLANNING READY`, confirm:

1. Implementation Source/current Authority is unambiguous enough and mixed source roles are normalized without suggestion→Requirement drift.
2. Material Current Reality/domain-workflow facts were inspected.
3. CONTRACT projects rather than redesigns.
4. Goal Horizon != Active Stage; no authorized Horizon was silently moved to FUTURE.
5. Every important active Requirement/invariant has adequate observable Acceptance, including Material variants and a credible observation path/precondition.
6. Planning assumptions are grounded or OPEN/UNKNOWN with triggers.
7. Implementation Commitments (architecture/dependency/safety-recovery-confirmation ordering/input/proof boundary) are explicit enough for Execution, but local mechanics are not over-scripted.
8. Remaining blockers route to the correct owner/input boundary.
9. Fresh Execution can begin from four Core + Current Reality; old history is not required wholesale.
10. If Horizon remains, Continuation Anchor/reacquisition is sufficient; Material upstream Waypoints/ordered value path were not silently discarded.
11. CONTRACT / ACCEPTANCE / WORKPLAN carry the same new Core Generation; no mixed generation is declared Planning Ready.
12. CONTRACT `Controller Revision` matches the Current fixed EXECUTION header; stale/missing controller binding is not Planning Ready.
13. No Material contradiction exists across CONTRACT / ACCEPTANCE / WORKPLAN (for example, proof obligation requiring behavior the Contract forbids); contradiction routes back to Planning/Design owner before effects.
14. No ordinary-user burden was added merely for implementation convenience when a contract-preserving lower-burden path exists.

Leave populated `.flow-mini/` four-Core in the target project. Package only Material non-secret transferable inputs; otherwise keep durable reacquisition locators.

End at **PLANNING READY**. Do not implement.
