# Fluid Progress Orchestration v0.1 Candidate — 破壊的設計レビュー

## 0. 判定

### 構想判定: **GO**

Fluid Progress Orchestration（FPO）の中心発想は進める価値がある。特に次は捨てるべきではない。

- 6つのcheckpointを「現在も成立を主張できる地点」として扱うこと
- Evidence保存前にcheckpointを進めないこと
- J1を単純Routingに留めること
- 外部Capabilityが自己申告だけでcheckpointやAcceptanceを変更できないこと
- Researchを固定phaseではなくCapabilityとして扱うこと
- P5を通常Authorityへ戻すRecovery Hubとすること
- Human-Last / Safety-First
- 詳細stateをControl Coreへ抱え込まないこと

### 現Candidate判定: **NO-GO for long-running runtime / real side effects**

v0.1 Candidateをこのまま長時間Agent実行、実環境変更、外部公開、金銭・権限を伴うOperationへ進めてはいけない。

ただし、捨てるべきCandidateではない。正確な位置づけは次である。

> **FPO v0.1は、良いPolicy Kernelと未完成なExternal Operational Planeを持つ設計Probeである。**

次の正しい進路は、CoreへP/J/M/checkpointを足すことではなく、外へ追い出したstateを責任別に契約化する **v0.2 Architectural Hardening** である。その後に決定論的fault injection、sandbox E2E、adversarial testへ進む。

---

## 1. レビュー方法

Google DriveのCURRENTとして確認した `多角マップ_v0.4.4_runtime.zip` を使用し、Mode H（Hybrid）で実施した。

### 問い固有の多角マップ

1. **目的・適用境界** — FPOが本当に解く問題、万能性の条件、そもそも不要な構成
2. **Achievement / Operation / Blocker state** — 6 checkpointで表すべきものと、外部へ別に持つべきもの
3. **Authority / Human / User control** — 誰が何を決め、誰が変更し、誰が止められるか
4. **Failure / Recovery / Side effect** — 診断、rollback、retry、compensation、No Progress
5. **Evidence / Acceptance / Evaluation** — false close、staleness、独立性、再現性
6. **Security / Trust boundary** — Web、Return、Capability、外部MDを攻撃者として見た場合
7. **Resource / Context / Long-running operations** — cost、token、時間、resume、context肥大
8. **運用・保守・移行** — schema、commit、audit、version、retention
9. **重複・圧縮・不要化** — Runtimeに不要な文書、規範重複、資産化のcritical path

各方向を分けて掘り、最後に依存関係を統合した。

### 外部先例・構造同型

- Agent2Agent Protocol: 外部Agent taskの明示的lifecycle、cancel、stream/update、auth
- Temporal: crash/network failure後に再開できるdurable execution
- Erlang/OTP Supervisor: retryを無限にせずrestart intensityで境界を持つ
- Saga / Compensating Transaction: 部分成立した外部副作用の補償
- OWASP GenAI/LLM risks: Prompt Injection、Improper Output Handling、Excessive Agency、Unbounded Consumption
- Anthropic Agent Evals / Long-running Harness: repeated trials、end-state、cost、component deletion test
- τ-bench: final stateとmulti-trial reliability
- LongRCA / TrajDebug / Failure as a Process: 長軌跡のroot cause特定と早期検知の難しさ（2026年の新しいpreprintであり、設計根拠の補助としてのみ使用）

---

## 2. 静的確認結果

- Markdown files: **30**
- Manifest entries: **29**（Manifest自身を除く）
- Manifest SHA-256 mismatch: **0**
- Missing Markdown references: **0**
- Runtime E2E: **未実施**
- Architecture validity: **未証明**

したがって、現Candidateの「静的PASS」は次の意味に限定される。

> ファイル同一性・参照整合は成立している。自律完走、Recovery品質、Human-Last、安全性、Runtime durabilityは成立したとは言えない。

詳細は `FPO_v0.1_Static_Analysis.json` を参照。

---

## 3. 粉々にした後にも残ったLoad-bearing Core

### 3.1 6 checkpointは残す

`none / defined / designed / executed / accepted / closed` は、世界の詳細状態ではなく「その地点まで現在も成立を主張できる」というAchievement stateとして筋がよい。

問題はcheckpointが少ないことではない。別責任のstateまでcheckpointへ押し込もうとしたことである。

### 3.2 Worker self-accept禁止は残す

外部Agentの `completed`、Validatorの `PASS`、Researchの提案をFPO側の成立判定と分離した点は強い。これはAuthority衝突とprompt injectionのblast radiusを抑える中核原則になる。

### 3.3 P5 Recovery Hubは残す。ただし細くする

P5は「修正を全部する場所」ではなく、Blocker caseを所有し、必要Evidenceを増やし、通常Authorityへ戻す場所として有効である。

ただし、成果物変更はP3、設計変更はP2、定義変更はP1、AcceptanceはP4に戻さなければならない。

### 3.4 State outside, policy insideは残す

この原則は正しい。ただし現在は、外部化した複雑さの契約が薄い。

> **複雑さは消えていない。Coreの外へ移動しただけである。**

FPOの次の仕事は、その外部stateをControl Coreへ戻すことではなく、外部のまま責任別に分離・契約化することである。

---

## 4. 統合して初めて見えた上位構造

現在のFPOはAchievement stateとその他すべてを二分している。しかし、実走行には最低でも次のstate planeが必要である。

```text
1. Achievement Plane
   none → defined → designed → executed → accepted → closed

2. Work Control Plane
   active / suspended / canceling / terminated / archived
   terminal reason: completed / canceled / aborted / unsatisfiable / out_of_budget ...

3. Delegated Operation Plane
   prepared / submitted / running / waiting_input / waiting_auth
   succeeded / failed / canceled / rejected / timed_out / unknown

4. Active Blocker Plane
   open / investigating / waiting / resolved / superseded

5. Evidence Plane
   proposed / valid / superseded / contradicted / retracted

6. Effect Plane
   intended / started / confirmed / unknown / compensating / compensated
```

これらは**新しいJ1 checkpointではない**。J1が直接Routingに使うAchievement stateと、外部実行・診断・監査のstateは別物である。

この分離をすると、FPOの「6 checkpointを維持する」と「長時間Operationを正しく扱う」が両立する。

---

## 5. BLOCKER — Hardening前に進めてはいけない問題

### B-01 外部Capabilityの実行ライフサイクルがない

`Dispatch → Return(status: completed)` しかなく、実行中、入力待ち、認証待ち、失敗、取消、成否不明、timeout、部分結果を表せない。

#### 壊れ方

```text
P3がD-001を保存
↓
Capabilityへ送信
↓
Capabilityは実行中
↓
FPO/Runtime crash
↓
再開時checkpoint=designed, interrupt_ref=null
↓
J1はP3を選ぶ
↓
同じ仕事を再送
```

副作用がなくても二重計算・二重artifactが起きる。副作用があればさらに危険である。

#### 必要な修正

`DISPATCH_RETURN_CONTRACT` を `DELEGATED_OPERATION_CONTRACT` へ置換し、logical intentとattempt、非終端/終端state、cancel、heartbeat/lease、deadline、duplicate/out-of-order Returnを定義する。

### B-02 成功以外の有限終端がない

FPOは「有限work」を掲げる一方、accepted以外でworkを終える方法がない。実現不能、取消、安全停止、予算切れは永久Suspendになる。

必要なのはFAILED/CANCELEDをAchievement checkpointへ足すことではない。外部Work Control Planeへterminal dispositionを持つことである。

### B-03 Active Blockerを集合として扱えない

複数Blockerを一つの参照へまとめられるが、個別status、依存、scope、resolution evidenceがない。一つ直して `interrupt_ref=null` にすると残りまで消える。

### B-04 Durable commit / replayが未定義

MDへ外部化したことで、次が必要になった。

- Recordとpointerのpublish順
- state_revision / expected_revision
- commit_id
- append-only event/decision log
- orphan Recordの扱い
- crash後のprojection再構築
- schema migration

具体的なlock実装はRuntimeへ任せてよいが、**どの状態が意味上commit済みか**はFPO契約が要求しなければならない。

### B-05 Trust boundaryが文章上の注意に留まる

「WebやReturnを上位命令として扱わない」は必要だが、LLMに同じcontextで読ませるだけでは防御にならない。

Control領域とUntrusted Return inboxを物理・論理分離し、schema validation、least privilege、secret handle、path allowlist、sandbox/egress、output sanitizationを必要条件にする。

### B-06 Evidence contractが薄い

Evidenceはファイル参照ではなく、**どのclaimを、何のrevisionで、どの方法・環境・trust domainから、いつ、どの範囲まで支えるか**を持つ必要がある。

特に「別Capability」は独立とは限らない。同じモデル、同じログ、同じ誤前提ならCross Checkは相関した二重自己確認にすぎない。

### B-07 Side effectの補償がない

重複防止・成否照合は強いが、部分成立した外部変更を取り消す/前進回復する契約がない。Sagaの原理どおり、compensatable / pivot / irreversibleを区別する必要がある。

### B-08 Recovery Authorityが重なる

- J3: 回復経路を選ぶ
- M07: 対応経路を選ぶ
- P4: 一部失敗なら直接rollback
- P5: Recovery Hub

このままでは、P5がtargetを変更したのにexecutedを維持する事故が起こり得る。

必要な境界:

```text
J3  = 原因分類 + 必要module/capability class
M07 = 継続/切替/待ち/Humanのpolicy
P5  = Blocker case所有 + rollback採用
P2  = design変更
P3  = target/artifact変更
P4  = Acceptance + 事前定義failure route
```

### B-09 Autonomy Budgetがない

No Progressは同一路線を止めるが、全体の試行・時間・cost・tokenを止めない。LLMは「少し違う戦略」を無限生成できる。

Human-Lastを成立させるには、Humanを呼ばない時間を無限にするのではなく、**有限budget内で自律的に最大限解く**必要がある。

### B-10 Decision Policy / Intent Fidelityがない

P1の最大の弱点は曖昧さではなく、P1が誤ったdefinitionを作っても、その後すべてがそのdefinitionに対して正しく動けることである。

原要求を不変sourceとして保存し、definition coverage、仮定、設計裁量、trade-off優先順位、棄却解釈を追跡する必要がある。高曖昧・高影響時は独立なDefinition Fidelity checkを行う。

### B-11 User controlとApproval lifecycleがない

Human-Lastは「ユーザーが止められない」を意味しない。

Cancel / Pause / Resume / Rebase / Requirement change、承認scope/expiry/revocation、実行中Operationへのcancel伝播を外部Work Controlへ追加する。

### B-12 Runtimeと開発文書が混在する

`STATIC_REVIEW`、E2E plan、Overview、templatesはRuntime Control Contextではない。多角マップ自身が行っているようにRuntime Manifestを分けるべきである。

---

## 6. HIGH — 構想の精度・効率を壊す問題

### H-01 ProgressのGoodhart化

「新Evidence」「新Capability」「新戦略」はProgressではなく候補である。

Progress claimは、対象Blockerへのmaterial relevance、採用済み変化、不確実性の減少、失効したEvidence、cost/risk/debtを含むnet changeとして残す。

### H-02 Root cause modelが薄い

長い軌跡では、最終症状と最初の決定的誤りは離れる。Blockerにsymptom、earliest unrepaired error、contributing cause、detection gap、resolution status、handoff refsを持たせる。

### H-03 Capability fitness/governanceが薄い

Registryに存在するだけでは選べない。health、availability、cost/latency、quality/eval history、security scope、compatibility、cancel/retry semantics、trust/provider、fallbackが必要である。

### H-04 P3内の部分実行単位がない

Project Graphを入れなくても、one work内にstable execution step ID、dependencies、adoption status、operation refは必要である。これはP3 crash/resumeの最低条件である。

### H-05 Context projection/compactionがない

外部MDへ出したことと、必要情報を正しく再取得できることは別である。Current projection、open obligations、adopted refs、recent events、archive、compaction source refsを持つ。

### H-06 E2E planが評価として不足

T1〜T7は良い障害カテゴリだが、単発scenarioである。次を追加する。

- deterministic protocol/fault tests
- positive + should-not-trigger negative cases
- repeated trials
- reference end-state / grader calibration
- baseline（v0.6、simple agent、FPO ablation）
- pass@1 / pass^k
- false-close / unsafe action / human intervention / wrong rollback
- token / time / cost

### H-07 Validation method変更の自己正当化

代替Evidence採用時はmethod revisionとcoverageを記録し、変更前より弱くない根拠を別に持つ。変更後の試験だけで変更自体を正当化しない。

### H-08 Risk Tierがない

当面は適用範囲をbounded digital workへ限定する。医療・法務・金融・公開・個人情報・物理操作等はrisk profileに応じてHuman gateを前倒しする。

### H-09 P6資産化がclosure critical pathにある

FPOのNorth Starに資産化は必須ではない。v0.1ではassetizationをoff-by-defaultのpost-actionまたは別workへ外す方が、無駄と共有資産汚染を減らせる。

### H-10 一つのBlockerがwork全体を止める

v0.1の逐次安全設計としては許容できる。ただし汎用性の境界として明示し、Blocker scopeを記録する。将来のplan unit化で局所Blockerへ拡張する。

---

## 7. MEDIUM — 無駄・重複・保守負債

1. Manifestはidentityだけ、Overviewはnon-normative、J/P/Mと外部Contractを正本にする。
2. 「推奨YAML」ではなくschema_version付きの必須schemaにする。
3. 全Recordへactor/time/sequence/state revision/bundle revisionを共通headerとして付ける。
4. `STATIC_REVIEW`を`STATIC_INTEGRITY_CHECK`へ改名し、Architecture/Runtime未証明をStatusへ出す。
5. P5は`回復・例外`へ改名し、旧名aliasで移行する。
6. G3は「新achievement checkpointを根拠なく増やさない」へ修正する。
7. 当面の公開claimを「bounded, digitally observable, single-work completion」へ狭める。
8. closed後のretention/GC/redaction/legal holdを定義する。

全件は `FPO_v0.1_Issue_Register.csv` を参照。

---

## 8. 進めるための最小再構成

### Control Coreは増やさない

- checkpoint 6個を維持
- J1を維持
- P1〜P6を維持
- J2/J3/M群を維持

### 外部契約を責任ごとに硬化する

1. `RUNTIME_MANIFEST.md`
2. `WORK_CONTROL_CONTRACT.md`
3. `DELEGATED_OPERATION_CONTRACT.md`（現Dispatch/Returnを置換）
4. `ACTIVE_BLOCKER_CONTRACT.md`
5. `EVIDENCE_CONTRACT.md`
6. `EFFECT_RECOVERY_CONTRACT.md`
7. `TRUST_AND_CAPABILITY_CONTRACT.md`（Registryを吸収/強化）
8. `実行基盤契約.md`改訂（commit/replay/event ledger）

ファイル数を減らしたい場合も、責任は混ぜない。Schemaと例を同じ契約内へ置き、別templatesは生成物にすることで圧縮する。

---

## 9. 改訂後のValidation Gate

### Gate A — Static / Model Check

- schema validation
- authority matrix conflict 0
- reference/hash integrity
- achievement transition validity
- runtime/dev context separation

### Gate B — Deterministic Runtime Simulation

- crash at every commit boundary
- duplicate/out-of-order Return
- input/auth wait
- cancel/pause/rebase
- multiple Blocker partial resolution
- stale/contradictory Evidence
- side-effect unknown/compensation
- budget exhaustion

### Gate C — Sandboxed Repeated E2E

- small software tasks
- positive/negative trigger pairs
- baseline and ablation
- repeated trials with pass@1 and pass^k
- completion, false-close, human calls, recovery yield, cost/time/token

### Gate D — Adversarial Safety

- prompt injection in Web/Return/artifact
- malicious/overprivileged Capability
- secret/data exfiltration attempt
- evaluator self-approval
- unsafe Human-Last continuation

### Gate E — Boundary Expansion

- research report
- document/data transformation
- GUI/tool task
- only after these pass, “general-purpose” claimを広げる

### Zero-tolerance guard

- unauthorized/high-impact side effect
- worker self-accept
- stale Evidenceによるfalse close
- duplicate irreversible effect
- user cancel無視

性能閾値は初回から恣意的な数字を固定せず、baselineとの差、guard違反ゼロ、複数trialの一貫性で決める。

---

## 10. 最終回答

### この構想は進められるか

**進められる。しかも中核はかなり強い。**

ただし進め方を間違えると、FPOは「小さいCoreの外側に、仕様のない巨大Runtimeを隠しただけ」になる。

正しい次の一手は次である。

> **FPO v0.1を完成版扱いせず、Policy Kernelとして凍結する。v0.2でExternal Operational Planeを契約化し、決定論的fault injectionから始める。**

### いま捨てるべきもの

- Runtime bundle内のSTATIC_REVIEW/E2E/説明文
- `status: completed`だけのReturn model
- 「stateを増やさないこと自体が成功」というG3
- 必須でないP6資産化のcritical path
- 正本が重複する説明文

### いま残すべきもの

- 6 Achievement checkpoints
- Evidence before checkpoint
- Authority分離
- P5 Recovery Hub
- Research as Capability
- Human-Last / Safety-First
- State outside, policy inside

この形なら、FPOは「万能Agent」ではなく、**接続能力を交換しながら、bounded workを成立まで運ぶ汎用Progress Policy**として十分に育つ可能性がある。

---

## 11. 参照した外部原理

- Agent2Agent Protocol Specification v1.0 — task lifecycle / cancel / streaming / authorization
- Temporal Documentation — durable execution and resume after failures
- Erlang/OTP Supervisor — restart strategy and maximum restart intensity
- Azure Architecture Center — Saga / Compensating Transaction patterns
- OWASP GenAI / LLM Top 10 — Prompt Injection, Improper Output Handling, Excessive Agency, Unbounded Consumption
- Anthropic, Demystifying Evals for AI Agents
- Anthropic, Harness Design for Long-Running Application Development
- τ-bench, arXiv:2406.12045
- LongRCA Bench, arXiv:2608.15242（2026 preprint）
- TRAJDEBUG, arXiv:2608.06346（2026 preprint）
- Failure as a Process, arXiv:2607.09510（2026 preprint）
