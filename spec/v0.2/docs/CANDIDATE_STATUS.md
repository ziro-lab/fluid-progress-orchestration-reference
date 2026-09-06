# FPO v0.2 Candidate Status
## 2026-08-25 — Architectural Hardening Baseline

## 判定

**ARCHITECTURE / CONTRACT / MACHINE-SCHEMA: PASS AS DESIGN CANDIDATE**  
**SANDBOX RUNTIME E2E: NOT EXECUTED**

v0.2は、v0.1で確認されたControl Coreの強さを維持し、外部Operational Planeの主要な契約不足を閉じた比較基準である。長期実環境変更へ直接投入するRuntimeではない。

## 固定した姿

```text
6-checkpoint Achievement Plane
  none → defined → designed → executed → accepted → closed

Small Policy Kernel
  J1 / P1–P6 / J2 / J3 / M02–M07

External Operational Plane
  Work Definition / Validation Method / Execution Plan
  Work Control / Approval / Budget / Terminal
  Dispatch Packet / Operation / Return
  Blocker / Progress / Evidence / Verdict
  Effect / Compensation / Trust / Capability
  Commit / Projection / Replay / Archive
```

## 現在通過したGate

- Runtime Manifest coverage/hash: PASS
- Runtimeとdevelopment/review contextの分離: PASS
- 6 Achievement checkpoint維持: PASS
- Authority ownerの一意性: PASS
- 24 immutable Record types + 2 Boundary Messages: PASS
- 26 canonical/schema fixtures: PASS
- exact Dispatch Packet digest binding: PASS
- exact Return digest binding: PASS
- canonical semantic Commit coverage/digest: PASS
- immutable Budget/Unit source vs projection cache: PASS
- machine schema reproducible generation: PASS
- Static checks: **30 / 30 PASS**
- Deterministic invariants: **64 / 64 PASS**

## v0.1レビューIssueの状態

B-01〜B-12およびH-01〜H-09はContract/Schema/Fixtureへ対応済み。H-10のglobal blocker / single-work limitationは明示的制約として受容し、Multi-workは導入していない。

「対応済み」はRuntimeで有効性が証明された意味ではない。各Issueの証明義務は`validation/TRACEABILITY_MATRIX.md`と`validation/FAULT_INJECTION_MATRIX.md`へ接続している。

## まだ証明していないもの

- LLM/Agentが曖昧要求から正しいDefinitionを安定生成すること
- 長い軌跡でのroot-cause accuracyとwrong rollback率
- real filesystem / queue / lock / crash / concurrency durability
- malicious Web/Return/Artifactに対するprompt-injection耐性
- Capability providerの実cancel/reconcile挙動
- repeated E2Eのpass^k、cost、Human介入率
- non-software domainでの一般性
- Multi-work / Project Graph

## 次の唯一のPromotion Gate

`docs/NEXT_RUNTIME_PROBE.md`の極薄Sandbox Probeを実装し、Fault Injection F-01〜F-32を段階投入する。

次段階でもCore増築を既定にしない。失敗したContract、Schema、Projection、Runner mechanismだけを特定し、load-bearingな変更だけを採用する。
