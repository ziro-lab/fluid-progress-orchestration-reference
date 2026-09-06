# FPO v0.2 Reference Flow

## 1. Normal completion

```text
Source Request
  ↓ P1: coverage + AC + Decision Policy
Defined
  ↓ P2: Plan Units + Validation Method + Effect plan
Designed
  ↓ P3: exact Dispatch Packet + Operation lifecycle + Target adoption
Executed
  ↓ P4: criterion verdicts
Accepted
  ↓ P6: no blocker/inflight/unknown effect + handoff
Closed + Work Control terminal/completed
```

## 2. Research Gap

```text
P1/P2 detects missing current fact
  ↓ Active Blocker Set
J1 → P5
J3 selects Research Capability class
M07 checks budget/risk
Operation runs in Untrusted Inbox
P5 adopts fact/evidence candidate
Blocker resolved
P1/P2 resumes and owns definition/design change
```

## 3. Crash after dispatch

```text
Dispatch Packet + Operation(prepared/submitted) committed and digest-bound
Capability continues
Runtime crash
  ↓ restart
Commit ledger reconstructs Operation=running
Provider/heartbeat queried
No duplicate dispatch
Late Return validated against current refs
Owner adopts or archives as stale
```

## 4. Wrong Design

```text
P4 sees FAIL
P2 Validation method / failure route says redesign, or cause is ambiguous
  ↓
ambiguous → Blocker/P5
P5 diagnoses design cause
P5 rolls checkpoint to defined
P2 changes Design
P3 re-executes current affected steps
```

## 5. Unknown Effect

```text
Effect started
Response lost
  ↓ state=unknown
No retry / no close
P5 reconciles external world
  ├ confirmed → continue
  ├ failed → retry if allowed
  └ partial → compensate or forward recover
```

## 6. User cancel

```text
Control Event(cancel)
  ↓ lifecycle=canceling
Runtime stops new dispatch / new Effect
active operations receive cancel
unknown effects reconciled
final cancellation settlement
lifecycle=terminated / disposition=canceled
checkpoint remains last valid achievement
```

## 7. Multiple blockers

```text
BLK-A Authority Gap = waiting
BLK-B Evidence Gap = investigating
  ↓
BLK-B resolved
BLK-A still waiting
interrupt_ref remains non-null
Unrelated event does not resume
Approval event resolves BLK-A
P5 clears set and resumes J1
```
