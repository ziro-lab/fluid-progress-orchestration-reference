# Fluid Progress Orchestration (FPO)

**A control and reliability harness for moving bounded AI work toward verified completion without giving every worker authority over the whole job.**

FPO is designed less to make a model *smarter* and more to make orchestration failures harder to silently promote into success. It keeps work state, authority, delegated operations, evidence, effects, recovery, and completion claims explicit enough to inspect, reject, resume, or reroute.

FPO grew from a small generic work-completion skeleton (汎用骨格) and hardens that minimal structure into a practical experimental runtime architecture.

> FPO is experimental. This repository is a reference architecture, reference runtime/probe surface, and evidence anchor—not a blanket production-safety certification.

## Quick start

The repository currently includes a deterministic Phase 0 reference probe. It is **not** packaged as a one-command general autonomous-agent product.

Current reference environment: Windows + Python 3 + Windows PowerShell.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\reset_workspace.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\check_environment.ps1
python .\runtime\run_baseline.py manifest
python .\runtime\run_baseline.py run
```

A successful baseline run should report `status: PASS` and finish at `checkpoint: closed`.

See **[GETTING_STARTED.md](GETTING_STARTED.md)** for the full walkthrough, verification command, generated run tree, and the boundary between the deterministic probe and real host integration.

## When FPO is useful

FPO is most relevant when a work item is bounded but the *control problem* matters—for example when you care about:

- explicit ownership of Definition, Design, Execution, Acceptance, Recovery, and Closure;
- rejecting stale, duplicate, or out-of-order delegated results;
- independent validation before success is accepted;
- interruption/resume without depending on conversation transcript memory;
- external Effects that must not be blindly retried after an unknown outcome;
- bounded Human escalation instead of silently guessing through authority or evidence gaps;
- parallel or multi-worker execution where fan-in, currentness, and mutation safety matter;
- recovery that can roll work back to the correct owner without turning the recovery stage into a universal executor.

You probably **do not need FPO** for a small one-shot task where ordinary model/tool execution is already cheap, reversible, observable, and easy to retry.

## How it works

FPO separates a small **Achievement Plane** from richer operational state.

```text
Achievement Plane

none -> defined -> designed -> executed -> accepted -> closed

              +

      small J / P / M policy kernel

              +

external operational state and contracts
Definition / Plan / Work Control / Operation / Blocker
Evidence / Effect / Trust / Capability / Commit / Projection
```

The normal control loop is deliberately not `P1 -> P2 -> P3 -> ...` by direct stage chaining:

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

This means a stage does not gain authority to execute the next stage merely because the next step looks obvious.

For a full behavioral explanation—including rollback, blockers, stale Returns, Effect handling, Human boundaries, parallel fan-in, and Settlement—read **[RUNTIME_BEHAVIOR.md](RUNTIME_BEHAVIOR.md)**.

## J / P / M in one minute

- **J1** routes trusted current state to the next owning P stage.
- **J2 / J3** select only the methods, knowledge, or Capability classes needed by P2 / P5.
- **P1** owns work Definition.
- **P2** owns Design and the Validation Method.
- **P3** owns Execution, Target/Artifact change, and Return adoption.
- **P4** owns criteria verdicts and Acceptance.
- **P5** owns blocker diagnosis, recovery-route adoption, and diagnostic rollback—but does not advance checkpoints.
- **P6** owns Settlement and successful Closure.
- **M modules** provide selectively loaded method/policy knowledge; they do not own checkpoints or replace P-stage authority.

J/P/M are **logical responsibility classes**. A host may package them as skills, files, or loader resources, but that packaging does not make them equivalent capabilities or give them the same authority.

## What FPO is trying to prevent

A normal successful run may look almost the same with or without FPO. The architecture is aimed at the cases that otherwise become expensive or misleading:

- a worker reports success before independent validation;
- a recovery path changes the design or target without the owning stage adopting it;
- stale or duplicate delegated results are treated as current;
- contradictory or insufficient Evidence is promoted into Acceptance;
- an external Effect is retried without knowing whether the first attempt already happened;
- a resumed run restarts from transcript memory or repeats completed work;
- a model/tool Return attempts to mutate Control State through untrusted text;
- parallel workers are individually current but still conflict through shared mutation or semantic invariants;
- pre-integration validation is incorrectly reused as proof of the integrated result.

The intended benefit is therefore less **higher peak intelligence** and more **lower orchestration failure variance**.

## Parallel execution

Parallelism is not tied to Flow Mini.

FPO's Parallel Profile defines safety/conformance requirements around execution binding, child identity, Effect mediation, settlement, immutable fan-in, and validation of the exact integrated revision. A compatible Provider can bind generic workers or another capability implementation without changing FPO Core authority.

Conceptually:

```text
FPO P2 Plan
   |
   v
FPO P3 delegated operations
   |
   v
Parallel Provider
   |-- Worker A
   |-- Worker B
   `-- Worker C
         |
         v
   frozen Integrated Revision
         |
         v
FPO P3 adoption -> FPO P4 independent validation
```

See `profiles/parallel-model/v0.1.4.2/` for the current Parallel/Profile material.

## Flow Mini integration

Flow Mini is an **optional implementation-stage capability integration**, not a prerequisite for FPO and not the source of FPO's authority model.

The repository records a current FPO × Flow Mini composition in **[CURRENT_FLOW_MINI_COMPOSITION.md](CURRENT_FLOW_MINI_COMPOSITION.md)**. In that composition, Flow Mini can own implementation-local planning/supervision while FPO retains work-level Definition, Control, Return adoption, Acceptance, Recovery, and Settlement.

A Flow Mini `DONE` or local stage acceptance is not automatically FPO `accepted` or `closed`.

## Reference probe vs. real integration

The checked-in `runtime/run_baseline.py` is intentionally a **deterministic probe harness, not a general orchestrator**. Its canonical P1/P2 decisions are fixed probe inputs so runtime behavior can be reproduced and inspected.

For real work, an FPO-compatible host needs to provide or bind the surrounding mechanics that the architecture expects, including current trusted state, owner-stage execution, durable records/commits, Capability/Provider binding, and external Effect mediation where applicable.

The architecture is therefore usable as a control/reference contract even when the host implementation differs from the checked-in Phase 0 probe.

## Evidence status

This repository contains recorded evidence through the Phase 7 line, but **proof scopes are intentionally narrow**.

Recorded/proven work includes, depending on phase:

- deterministic normal-flow runtime behavior;
- crash durability and adversarial state-consistency probes;
- control, budget, and trust-boundary tests;
- real-AI capability and research trials;
- Human-Last boundary tests;
- multi-generation handoff and interruption/resume trials;
- material-progress / repeated-recovery probes;
- naturalistic E2E fixtures;
- a recorded real-AI fixed Flow Mini integration path;
- Parallel Profile conformance work and a recorded local-adapter/provider parallel trial.

Important limits:

- recorded Phase 7C evidence is **not** blanket proof of the current live Codex Plugin or Same-Sol Host path;
- parallel efficiency is not characterized by the recorded local-adapter Phase 7C run;
- long-horizon autonomy and real irreversible Effects remain outside the proven scope;
- AI-agent reliability, malicious-input resistance, real provider/network behavior, and non-software generality are not globally proven;
- historical "hidden oracle" fixtures were hidden from workers during their recorded runs, but once published they must not be treated as hidden for future replay claims.

For exact status and scope, read **[STATUS.md](STATUS.md)** and the relevant `phase*/` reports before extending any claim. Public copies of some historical evidence have environment-specific local user-home paths normalized for publication; see **[PUBLICATION_NOTES.md](PUBLICATION_NOTES.md)**.

## Start here

If you want to **run something now**:

1. [GETTING_STARTED.md](GETTING_STARTED.md)
2. `runtime/run_baseline.py`
3. `probe/`

If you want to **understand behavior**:

1. [RUNTIME_BEHAVIOR.md](RUNTIME_BEHAVIOR.md)
2. `spec/v0.2/runtime/contracts/AUTHORITY_MATRIX.md`
3. `spec/v0.2/docs/REFERENCE_FLOW.md`
4. `spec/v0.2/runtime/core/WORK_STATE.md`

If you want to **understand the architecture and design choices**:

1. `spec/v0.2/docs/FPO_OVERVIEW.md`
2. `spec/v0.2/docs/ARCHITECTURE_DECISIONS.md`
3. `spec/v0.2/runtime/RUNTIME_ENTRY.md`
4. `spec/v0.2/runtime/RUNTIME_MANIFEST.md`

If you want to **inspect evidence**:

1. [STATUS.md](STATUS.md)
2. `evidence/`
3. the relevant `phase*/` directory
4. [PUBLICATION_NOTES.md](PUBLICATION_NOTES.md)

## Repository map

| Path | Purpose |
|---|---|
| `spec/v0.2/` | Current FPO v0.2 architecture/specification candidate |
| `spec/v0.2/runtime/` | Normative runtime entry, core, contracts, and schema |
| `runtime/` | Deterministic reference probe runtime |
| `probe/` | Canonical baseline fixtures and acceptance material |
| `capabilities/` | Bound capability examples/integration surfaces |
| `profiles/parallel-model/v0.1.4.2/` | Parallel + Provider safety/conformance profile |
| `evidence/` | Selected deterministic evidence summaries |
| `phase4a/` … `phase7c/` | Recorded experimental/proof-phase fixtures, results, and reports |
| `GETTING_STARTED.md` | How to run the checked-in reference probe |
| `RUNTIME_BEHAVIOR.md` | Public orientation to expected runtime behavior |
| `CURRENT_FLOW_MINI_COMPOSITION.md` | Current optional FPO × Flow Mini composition |
| `CONTRIBUTING.md` | Feedback and contribution guidance |
| `SECURITY.md` | Security reporting scope and guidance |
| `PUBLICATION_NOTES.md` | Clean-snapshot and public-copy redaction notes |

## Runtime boundary

The repository is intentionally larger than the runtime control context.

Historical phase material, evidence, reports, examples, and optional integrations are not automatically runtime authority. `spec/v0.2/runtime/RUNTIME_MANIFEST.md` defines the normative runtime surface for the current specification candidate.

## Feedback and contributions

Feedback is welcome, but never required for use under the license.

Reports are especially useful when they include real failure behavior, model-specific routing/authority violations, recovery problems, stale/currentness issues, duplicate Effects, false completion, or a simplification that removes cost without silently removing a guarantee.

A result that says **"FPO added complexity without material benefit here"** is also useful.

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for details.

## License

Licensed under the **Apache License 2.0**. See **[LICENSE](LICENSE)**.

Use, modification, and redistribution are permitted subject to the license terms. Reporting improvements or derivative work back to this project is appreciated, but it is not a condition of use.
