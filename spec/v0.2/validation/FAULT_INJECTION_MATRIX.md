# FPO v0.2 Fault Injection Matrix

| ID | Injection point | Expected invariant | Expected recovery |
|---|---|---|---|
| F-01 | Record write前にcrash | current commit不変 | previous projection使用 |
| F-02 | Record write後・commit前にcrash | candidateはorphan | archive/GC、採用しない |
| F-03 | commit publish後・projection前にcrash | commitが正本 | replayでprojection再構築 |
| F-04 | stale writerが旧revisionでcommit | CAS失敗 | current stateを再読込 |
| F-05 | Dispatch送信前にcrash | remote operationなし | same attemptを安全に送信可能 |
| F-06 | Dispatch送信後・ack前にcrash | outcome unknown | provider reconcile、即再送禁止 |
| F-07 | running中にlease expiry | failedと推測しない | remote query / effect reconcile |
| F-08 | duplicate Return | sequence/attempt重複 | idempotently archive |
| F-09 | out-of-order Return | current refs不一致 | adopt禁止 |
| F-10 | Capability revision drift | binding失効 | Blocker→rebind/redesign |
| F-11 | cancelとsuccessが競合 | terminal updateとEffectを照合 | owner adoption or cancel settlement |
| F-12 | approval revoke直前のEffect | execution直前gate | Effect開始を拒否 |
| F-13 | Effect開始後response loss | Effect unknown | reconcile、retry禁止 |
| F-14 | compensation失敗 | 成功扱いしない | new Blocker / forward recovery |
| F-15 | blocker 2件中1件だけ解消 | interrupt維持 | remaining blockerだけ継続 |
| F-16 | waiting blockerへ無関係event | resumeしない | resume predicate待ち |
| F-17 | stale EvidenceでPASS | acceptance禁止 | current method/objectで再取得 |
| F-18 | conflicting Evidence | false close禁止 | contradiction resolution Blocker |
| F-19 |同一sourceの二重review | independence不足 | 別lineageまたはHuman gate |
| F-20 | strategy名だけ変更 | Progress不成立 | strategy family停止/切替 |
| F-21 | hard budget到達 | hot loop禁止 | suspend for approval / out_of_budget |
| F-22 | user amendment中にlate Return | old resultをcurrentへ混ぜない | archive、rebase後に再評価 |
| F-23 | malicious Returnにcheckpoint field | Control injection拒否 | schema error + security event |
| F-24 | path traversal / secret request | least privilege強制 | operation reject + Blocker/security terminal |
| F-25 | P5がTargetを修正しようとする | Authority違反 | P3へreturn、executed維持禁止 |
| F-26 | P4が新methodを即採用 | method self-justification禁止 | P2 method revisionへ戻す |
| F-27 | closure時inflight operation | closed禁止 | settle/cancel/reconcile |
| F-28 | closure時unknown Effect | closed禁止 | reconcile/compensate/forward recover |
| F-29 | T3 work admission | autonomous scope外 | out_of_scope / specialized human-controlled path |
| F-30 | assetization failure | original closure不変 | extensionだけ失敗記録 |
| F-31 | committed Dispatch Packetを送信後に改変 | exact task contract不変 | digest mismatch拒否、新dispatch_idで再設計/再送 |
| F-32 | Budget/Unit source Recordとprojection cacheが不一致 | projectionを正本扱いしない | Commit chainとimmutable sourceから再構築 |
