# Phase 3 Fault Sequence

The faults are injected one at a time from fresh state. The harness does not
use wall-clock races, external network, credentials, real AI agents, or
irreversible effects.

## Gate A — Control Authority

1. E1 `pause-before-dispatch`
2. E2 `pause-running`
3. E3 `cancel-late-success`
4. E4 `requirement-amendment`
5. E5 `approval-revoked-before-effect`

## Gate B — Resource Budget

6. E6 `attempt-budget-exhaustion`
7. E7 `effect-budget-exhaustion`
8. E8 `budget-source-projection-drift`

## Gate C — Trust Boundary

9. E9 `return-control-injection`
10. E10 `artifact-control-injection`
11. E11 `capability-scope-escape`
12. E12 `manifest-external-override`

## Boundary rules

- Control events come only from the trusted user/control path.
- Capability Returns and Artifacts are immutable untrusted data.
- Immutable Budget source wins over projection cache drift.
- Manifest-external documents are not normative.
- A rejected attempt is counted as a rejection, never as a successful Effect.
