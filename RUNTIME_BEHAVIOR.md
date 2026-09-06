# FPO Runtime Behavior

This document explains the behavior an FPO-compatible runtime is expected to preserve. It is a public orientation guide, not a replacement for the normative files under `spec/v0.2/runtime/`.

## 1. The normal control loop

FPO does not treat P1-P6 as a script that directly calls the next stage.

The normal shape is:

```text
trusted current state
        |
        v
RUNTIME_ENTRY / Work Control gate
        |
        v
       J1
        |
        v
one owning P stage
        |
        v
records + semantic commit + projection
        |
        +--------------------> RUNTIME_ENTRY / J1 again
```

J1 routes; it does not perform the selected stage's work.

The ordinary Achievement path is:

```text
none
  -> P1 Definition
  -> defined
  -> P2 Design
  -> designed
  -> P3 Execution / Return adoption
  -> executed
  -> P4 Verification / Acceptance
  -> accepted
  -> P6 Settlement / Close
  -> closed
```

After a P stage commits its result, control returns to the runtime/J1 path. A P stage does not gain authority to directly execute the next P stage merely because the next checkpoint appears obvious.

## 2. What J2 and J3 do

J2 and J3 are selectors inside specific owner stages, not extra global workflow stages.

- J2 is used from P2 to select only the methods, knowledge, or Capability classes required to finish Design.
- J3 is used from P5 to select only the methods, knowledge, or Capability classes required to diagnose and recover from the current blocker.

M modules provide method/policy knowledge. They do not own checkpoints and do not replace P-stage Authority.

A host may physically package J/P/M files as skills or loader resources. That packaging does not change their logical responsibility.

## 3. Checkpoints are Achievement claims, not activity states

The six checkpoint values are intentionally small:

```text
none / defined / designed / executed / accepted / closed
```

They answer roughly:

> Against the current external world and adopted evidence, how far can this work still claim to be established?

They do **not** encode operational states such as:

- waiting;
- paused;
- canceled;
- failed;
- retrying;
- running child count;
- budget exhausted;
- no progress.

Those belong to Work Control, Operation, Blocker, Effect, Budget, and other operational records.

A checkpoint may move backward when a current premise becomes invalid. Existing external Effects are never assumed to have rolled back merely because the Achievement checkpoint moved backward.

## 4. What happens when work fails

FPO distinguishes deterministic validation routing from diagnostic recovery.

### Predefined P4 failure route

If P2 already defined an unambiguous validation-failure route and the observation matches it exactly, P4 may apply that predefined route.

Examples include:

- redefinition required -> `none`;
- redesign required -> `defined`;
- same Design must be re-executed -> `designed`;
- Target/Design unchanged and only validation repeats -> remain `executed`.

P4 does not invent a new recovery strategy.

### P5 diagnostic recovery

If the cause is ambiguous, outside the predefined route, based on conflicting Evidence, or otherwise requires diagnosis, the work becomes blocked and routes through P5.

P5 may:

- maintain blocker lifecycle;
- obtain diagnostic observations/research;
- distinguish causes;
- decide whether material progress occurred;
- adopt a recovery route;
- keep or roll back the checkpoint to the last currently valid Achievement point.

P5 does **not** directly take over the other owners' Authority. Definition changes return to P1, Design/Validation Method changes to P2, Target/Artifact changes to P3, Acceptance to P4, and successful closure to P6.

P5 never advances the Achievement checkpoint.

## 5. Capability and worker output are proposals until adopted

External tools, models, workers, Flow Mini, research calls, or other Capabilities do not become FPO Authority merely because they were invoked.

The intended boundary is:

```text
trusted Dispatch
    -> Capability / worker
    -> Return enters untrusted boundary
    -> schema/currentness/identity checks
    -> owning P stage adopts or rejects it
```

A worker saying `DONE`, `PASS`, or `SUCCESS` is not equivalent to:

- P3 adoption;
- P4 Acceptance;
- P6 Close.

Late, stale, duplicate, out-of-order, or superseded Returns may be retained as historical material but must not silently mutate current Control State.

## 6. Effects are separate from logical worker success

A successful worker response does not prove that a persistent/shared Effect is safely settled.

An FPO-compatible provider must preserve enough identity and observation to distinguish cases such as:

- Effect confirmed;
- Effect absent and safe to retry;
- Effect still running;
- Effect outcome unknown;
- Effect fenced or otherwise prevented from further mutation.

Unknown external outcomes are reconciled rather than blindly retried.

This becomes especially important with crash/restart and parallel execution.

## 7. Pause, cancel, approval, and budget happen before J1

Work Control lifecycle is checked before ordinary J1 routing.

If a work is suspended, canceling, terminated, over hard budget, or missing required approval, the runtime does not simply dispatch the next P stage because the Achievement checkpoint says one is next.

The runtime may perform mechanical settlement/reconciliation work while ordinary business-stage routing remains stopped.

## 8. Human-Last behavior

FPO tries to avoid sending mechanically resolvable decisions back to a human, but it does not guess through irreducible human boundaries.

A compatible runtime may continue autonomously when a question can be resolved from trusted current inputs, reversible defaults, observation, research, or an available Capability.

It should stop or suspend with an explicit narrow blocker when the missing item genuinely requires human preference, authority, evidence, or physical capability.

The expected behavior is therefore sometimes:

```text
not enough authority/evidence
-> explicit blocker / suspended
```

rather than a fluent but invented completion.

## 9. Parallel behavior

Parallel execution is an external composition of FPO-owned work, not a second FPO state machine.

A compatible Parallel Provider may:

1. bind exact current FPO/Capability refs;
2. spawn one or more children;
3. enforce physical/semantic conflict constraints;
4. mediate persistent Effects;
5. settle/fence child mutation paths;
6. fan results into a new exact Integrated Revision;
7. freeze/publish that exact revision through existing FPO surfaces;
8. return it for ordinary FPO adoption and independent validation.

Two important consequences follow:

- child success is not FPO Acceptance;
- validation of independent branches does not automatically validate the integrated result.

Flow Mini is one optional implementation-stage integration. Generic FPO parallelism does not require Flow Mini if another Provider/Capability satisfies the relevant contracts.

## 10. Completion behavior

P4 may move the work to `accepted` only when all current MUST criteria have sufficient current Evidence and no unresolved conflict/UNKNOWN blocks Acceptance.

P6 then performs settlement. Before `closed/completed`, the runtime must establish that the work is not hiding unresolved required operations, Effects, blockers, control events, or missing handoff material.

Assetization/reuse is not a closure requirement.

## 11. What a user should expect to notice

On easy successful tasks, FPO may appear to do very little differently from an ordinary agent.

The intended difference appears mainly around failure and uncertainty:

- fewer silent responsibility changes;
- fewer unverified success claims;
- more explicit blockers instead of guesses;
- stale delegated work rejected instead of adopted;
- failed validation routed to the correct owner;
- recovery that preserves Authority boundaries;
- safer crash/resume and Effect handling;
- independent validation before final Acceptance.

That means FPO can add bookkeeping and latency without visibly improving the best-case answer. The project is aimed primarily at reducing orchestration failure variance, not increasing peak model intelligence.

## 12. Normative sources

When this guide and a normative runtime file appear to disagree, use the current runtime source of truth:

- `spec/v0.2/runtime/RUNTIME_MANIFEST.md`
- `spec/v0.2/runtime/RUNTIME_ENTRY.md`
- `spec/v0.2/runtime/core/`
- `spec/v0.2/runtime/contracts/`
- `spec/v0.2/runtime/schemas/fpo_records.schema.json`

See `GETTING_STARTED.md` for the reference probe commands and integration entry points.
