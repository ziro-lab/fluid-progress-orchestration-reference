# Fault Injection Sequence

一度に複数 Fault を入れない。前段が PASS してから次へ進む。

## Phase 0 — Baseline

- Faultなしの正常完走
- duplicate Effect = 0
- false close = 0
- input不変

## Phase 1 — Crash durability

1. Dispatch Packet + prepared Operation commit後・送信前 crash
2. 送信後・remote ID保存前 crash
3. Operation running中 crash
4. success Return受信後・P3 adoption前 crash

## Phase 2 — Ordering / identity

5. Return duplicate
6. Return out-of-order
7. stale revision Return
8. committed Dispatch Packet mutation

## Phase 3 — Unknown / evidence

9. output write後・response loss → Effect unknown
10. Evidence conflict
11. source Record / projection cache drift

## Phase 4 — Control

12. User pause
13. User cancel
14. User amendment
15. Budget exhaustion

## Phase 5 — Trust

16. Return本文への control injection
17. malformed Return
18. wrong capability revision

## Promotion condition

各Faultで期待stateへ有限収束し、duplicate Effect / false close / stale adoption / invalid authority mutation が0であること。
