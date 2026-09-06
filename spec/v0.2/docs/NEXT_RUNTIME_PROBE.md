# Next Step — FPO v0.2 Sandbox Runtime Probe

## 目的

FPO v0.2のContractを実装し切ることではなく、最も荷重の大きい不変条件が、極薄Runtimeと実Agentで本当に成立するかを確認する。

## Probeの最小構成

```text
FPO Runtime Entry
  ├ read validated projection
  ├ append immutable record
  ├ publish semantic commit with CAS
  ├ rebuild WORK_INDEX
  ├ commit and hash one exact Dispatch Packet
  ├ invoke one delegated Capability with that Packet
  ├ receive immutable untrusted Return and bind its digest
  ├ query/cancel/reconcile Operation
  └ stop before unsafe Effect
```

業務判断、原因分類、AcceptanceをRunnerへ入れない。Runnerはmechanismだけを持つ。

## Canonical Probe Work

小さなローカル・テキスト変換ツールを対象にする。入力非破壊、別名出力、決定論的テストが可能で、外部Effectをworkspace内へ限定できる。

### Fault injection

1. Dispatch Packet + prepared Operation commit後・送信前crash
2. 送信後・remote ID保存前crash
3. Operation running中crash
4. success Return受信後・P3 adoption前crash
5. Return duplicate / out-of-order / stale revision
6. output write後・response lossによるEffect unknown
7. Evidence conflict
8. User pause / cancel / amendment
9. Budget exhaustion
10. Return本文へのcontrol injection
11. committed Dispatch Packet mutation
12. Budget / Unit source Recordとprojection cache drift

## Promotion Gate

- duplicate Effect 0
- false close 0
- stale Return adoption 0
- invalid Authority mutation 0
- crash後に一意なcommitted stateへ収束
- Cancelが有限terminalへ収束
- unknown Operation / Effectを推測成功しない
- Source→Definition coverage脱落 0
- Human interventionの必要/不要を分類可能
- Runtime ContextへManifest外規範を混入しない
- Dispatch Packet mutationをdigest mismatchとして拒否
- Budget / Unit projection driftをimmutable sourceから再構築

## Deliberately not included

- Multi-work / parallel scheduler
- UI automation
- public deployment
- irreversible external Effect
- assetization
- non-software domain

Probeが通って初めてSingle-domain Runtime Candidateへ進む。ここで失敗したContractだけを修正し、Coreの増築を既定にしない。
