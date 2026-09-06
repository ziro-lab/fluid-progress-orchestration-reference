# Getting Started with FPO

This repository contains the FPO architecture, runtime contracts, deterministic reference probes, and recorded evidence.

It is **not** currently packaged as a one-command autonomous-agent product. The checked-in `runtime/run_baseline.py` is intentionally a deterministic probe harness, not a general orchestrator: its canonical P1/P2 decisions are fixed probe inputs so that runtime, durability, authority, Effect, Evidence, and settlement behavior can be reproduced and inspected.

There are therefore two useful ways to start:

1. run the deterministic reference probe;
2. integrate the FPO runtime contract into an agent/host environment for real work.

## 1. Run the deterministic Phase 0 reference probe

### Current reference environment

The checked-in Phase 0 reference capability is Windows/PowerShell based.

Recommended environment:

- Windows;
- Python 3;
- Windows PowerShell available from the normal Windows installation;
- a fresh checkout or downloaded source tree.

The Phase 0 Python runner uses only the Python standard library. The reference worker is `capabilities/text_transform/worker.ps1`.

The architecture itself is not intended to be Windows-specific; this limitation belongs to the current reference probe/capability implementation.

### Step A — reset generated state

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\reset_workspace.ps1
```

This removes generated run directories and the canonical probe output.

### Step B — check the local reference environment

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_environment.ps1
```

Expected result:

```text
FPO Sandbox Starter environment check: PASS
```

This is only a lightweight local capability/environment check. It is not the FPO runtime proof itself.

### Step C — verify the Runtime Manifest

```powershell
python .\runtime\run_baseline.py manifest
```

Expected top-level result:

```json
{
  "status": "PASS"
}
```

The runner resolves the current checked-in specification from `spec/v0.2/` and verifies the Runtime Manifest boundary and file hashes before running the probe.

### Step D — run the canonical baseline

```powershell
python .\runtime\run_baseline.py run
```

A successful run returns JSON containing values equivalent to:

```json
{
  "status": "PASS",
  "checkpoint": "closed",
  "work_control_lifecycle": "terminated",
  "disposition": "completed",
  "run_path": "runs/<timestamp>"
}
```

The run also creates a durable run tree under `runs/<timestamp>/`, including immutable records, messages, commits, projections, evidence, and the final result.

The canonical capability converts `workspace/input.txt` to uppercase in the separate `workspace/output/output.txt` target while preserving the input.

### Step E — independently re-verify a recorded run

Use the `run_path` returned by the previous command:

```powershell
python .\runtime\run_baseline.py verify --run .\runs\<timestamp>
```

The verifier checks, among other things:

- schema-valid records;
- commit/CAS chain integrity;
- dispatch/Return digest binding;
- a single Effect/invocation;
- P3-owned Return adoption;
- Evidence before Acceptance;
- terminal settlement consistency;
- projection reconstruction.

## 2. What the reference probe does — and does not do

The Phase 0 runner demonstrates the runtime mechanics against one fixed bounded work item.

It **does demonstrate** the checked-in reference implementation of:

- Runtime Manifest validation;
- durable records and semantic commits;
- checkpoint progression;
- delegated operation identity;
- untrusted Return handling and owner adoption;
- bounded Effect handling;
- Evidence / Acceptance separation;
- final settlement and projection rebuild.

It **does not** take an arbitrary user request, call an LLM, and autonomously infer the complete FPO P1/P2/P3/P4/P5/P6 work. Do not treat a successful Phase 0 run as evidence that an arbitrary agent host will behave correctly.

Later phase directories contain additional recorded probes and AI/host integration evidence with their own explicit proof scopes.

## 3. Integrating FPO for real work

For an actual agent host, FPO should be treated as a control/runtime contract rather than as one giant prompt.

The host needs to provide the mechanics required by the current FPO runtime surface, including:

1. resolve and validate `spec/v0.2/runtime/RUNTIME_MANIFEST.md`;
2. enter through `spec/v0.2/runtime/RUNTIME_ENTRY.md`;
3. persist authoritative source records, commits, and reconstructible projections;
4. run the pre-routing Work Control gate before J1;
5. let J1 select only the next owning P stage;
6. load J2/J3/M material only when required by the owning stage;
7. bind concrete tools/agents/providers as Capabilities without granting them FPO Authority;
8. keep Dispatch and Capability Return identity/currentness explicit;
9. mediate persistent/shared Effects through a provider path that can reconcile unknown outcomes;
10. adopt Evidence and Acceptance only through the owning FPO stage;
11. route blockers/recovery through P5 rather than allowing workers to silently redesign the work;
12. settle and close only through P6.

The exact host integration is intentionally external to FPO Core. A Codex plugin, local agent runtime, custom orchestrator, CI host, or another provider can implement these mechanics as long as the relevant FPO contracts and Authority boundaries remain intact.

## 4. Parallel execution

Flow Mini is **not required** for FPO parallel execution.

The checked-in Parallel Profile separates FPO Authority from provider mechanics. A compatible provider may bind/spawn multiple children, mediate Effects, settle them, fan results into an exact Integrated Revision, freeze/publish that revision, and return it to ordinary FPO P3/P4 adoption and validation.

Flow Mini is one optional implementation-stage Capability/integration that can add its own implementation planning and supervision. It is not the source of FPO's generic parallel semantics.

See:

- `profiles/parallel-model/v0.1.4.2/01_PARALLEL_SAFETY_CONFORMANCE_v0.1.4.2.md`
- `profiles/parallel-model/v0.1.4.2/02_PROVIDER_IMPLEMENTATION_CONFORMANCE_v0.1.4.2.md`
- `CURRENT_FLOW_MINI_COMPOSITION.md` for the current optional Flow Mini composition.

## 5. Read next

For the expected control flow and failure behavior, read `RUNTIME_BEHAVIOR.md`.

For the architectural details, continue with:

1. `spec/v0.2/docs/FPO_OVERVIEW.md`
2. `spec/v0.2/runtime/contracts/AUTHORITY_MATRIX.md`
3. `spec/v0.2/docs/REFERENCE_FLOW.md`
4. `spec/v0.2/runtime/core/WORK_STATE.md`
5. `spec/v0.2/docs/ARCHITECTURE_DECISIONS.md`
