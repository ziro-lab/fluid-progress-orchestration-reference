# Flow Mini Entry — v0.5.0 Implementation Core Convergence Candidate r3

目的: **現在の仕事を、Flow Mini Coreへ最短で接続する。**

Flow Mini Coreは **Implementation Planning → Execution**。上流Designは所有しない。設計済みならそのCurrent sourceを直接使い、未設計ならOptional Bare Design Bootstrapまたは外部Design capabilityへrouteする。

## 0. First inspect

利用可能な範囲で次だけ確認する。

- user request / latest feedback
- current target project / artifact / Current Reality
- Currentな仕様・設計・Issue・Brief・Handoff等の **Implementation Source** の有無とcurrentness
- populated current-task `./.flow-mini/` の有無
- WORKPLANのCurrent Resumeと、accepted / incomplete / interrupted stateを裏づけるCurrent evidence

古いArtifactが存在するだけでCurrent扱いしない。

### Narrow-first route scan

EntryではProject historyを広く読まない。

- current v0.5 Coreがある場合、route判定は **CONTRACT + WORKPLAN + Core Generation headers + CONTRACTの`Controller Revision` + EXECUTION header + ACCEPTANCE/EXECUTIONの存在/currentness + target reality** から始める。ACCEPTANCE / EXECUTION本文はExecution route確定後に読む
- CONTRACT / ACCEPTANCE / WORKPLANの`Core Generation`がmissing/mismatchの場合はtorn/pre-r2 Planning stateとしてExecutionへ入れずPlanningへ戻す
- CONTRACTの`Controller Revision`がmissing、またはproject-local EXECUTION headerと一致しない場合はstale/torn ControllerとしてExecutionへ入れずPlanningへ戻す
- old Design / logs / completed attempts / prior Implementation Sourceは、Material mismatch・reopen trigger・source locatorが要求した場合だけ追加で読む
- stale / superseded materialをordinary working contextへ自動投入しない
- detail不足を推測で埋めず、必要なら最小のauthoritative sourceをreopenする

### DONE short-circuit

WORKPLANが`DONE`で、同じcanonical workのcontinuationであり、new request / amendment / scope change / Material Reality mismatchが無い場合は、同一workのExecution本文をロードせずterminal stateとして扱う。`DONE`単独は証拠ではない。

## 1. Route

### A — Execution

次をすべて満たす場合:

- populated Current v0.5 Implementation Coreがある
- Contract / Acceptance / Workplanとtarget realityにMaterialな取り違えがなく、Execution activation時のcross-Core contradiction checkを通せる
- userがimplement / build / continueを求めている
- Resume Statusがterminalではない

→ project-local `.flow-mini/EXECUTION.md`。

### B — Implementation Planning

次のいずれか:

- CurrentなImplementation Sourceがあり、Goal / Requirement / Scope / Settled Design / Acceptance meaning等をMaterialに再設計せず実装へ落とせる
- same upstream meaningのままREPLANが必要
- accepted Stage後、同じCurrent Goal Horizon内の次Stageをactivateする
- legacy Flow Mini stateをsame meaningのままv0.5へmigrationできる

→ `01_IMPLEMENTATION_PLANNING.md`。

Implementation Sourceは特定フォーマットを要求しない。Currentで意味が十分なら、仕様書・設計書・PRD・Issue・人間のBrief・外部Design SkillのHandoff等を直接使える。Planningはmixed sourceを軽く`Normative / Fact-Evidence / Reference-Suggestion / Open`へ正規化し、単なる提案をRequirement/Authorityへ昇格させない。

### C — Bare Design Bootstrap

Current Implementation Sourceがなく、rough / underspecified requestから普通の壁打ちで実装可能な設計を成立させれば足りる場合:

→ `bootstrap/BARE_DESIGN_BOOTSTRAP.md`。

BootstrapはFlow Mini Coreではない。Design Readyで止まり、そのBriefを**別のPlanning invocation/context**へ渡す。

### D — External Design Required

次のいずれか:

- userが高度なDesign review / UIUX exploration / broad research / destructive redesignを求める
- existing DesignのGoal / Requirement / Scope / Goal Horizon / settled choice / Acceptance meaning / AuthorityをMaterialに変える必要がある
- Bare Bootstrapでは責任を持って収束できないDesign ambiguityが残る

→ 利用可能な外部Design capabilityへrouteする。Flow Miniは特定Design Skillを内蔵・要求しない。

外部Designが完了したら、そのCurrent outputをImplementation SourceとしてBへ戻す。

## 2. Re-entry boundary

- task split/order、reversible local HOW、同じproof boundary/strength内のexact verification mechanics → **Planning-owned Implementation Commitments（dependency / safety / recovery / confirmation / irreversible-effect ordering等）を保つ限り**Executionで局所適応可能
- Active Stage boundary、implementation architecture/dependency basis、required input basis、Acceptance proof boundary/strengthをMaterialに変える → **REPLAN / Planning**
- Goal / Requirement / Product Scope / Goal Horizon / Settled Design / design-level Acceptance meaning / Authority / User-owned valueを変える → **DESIGN REENTRY REQUIRED**
- operational credential/path/permission/real-world input不足でDesign変更不要 → 必要な層で最小限確認

## 3. Anti-oscillation

上位へ戻すときは、**どのowner stateが変わる必要があるか**を一つ以上示す。

- REPLAN: current upstream meaningは維持できるが、何のimplementation plan basisが変わったか
- Design re-entry: どのDesign-owned semanticが影響されたか

同じFailureを言い換えただけで往復しない。新しいEvidence / changed basisなしにREPLAN↔Designを反復しない。

## 4. User-facing simplicity

通常ユーザーは「これ作って / 続きを進めて」でよい。Bootstrap / Planning / Execution等の内部Route名を覚えさせない。
