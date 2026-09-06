# Phase 1 — Crash Durability Evidence

Overall verdict: **PASS**

Fresh Phase 1 matrix completed C1–C4 successfully after strict manifest resolution was fixed.

| Case | Crash boundary | Last commit before crash | Reconcile | Invocation / Effect / Return / Adoption | Final |
|---|---|---:|---:|---:|---|
| C1 | after dispatch commit, before capability submit | COM-0004 | 1 | 1 / 1 / 1 / 1 | closed / completed |
| C2 | after provider submit, before remote ID persist | COM-0004 | 1 | 1 / 1 / 1 / 1 | closed / completed |
| C3 | operation running | COM-0004 | 1 | 1 / 1 / 1 / 1 | closed / completed |
| C4 | after immutable Return persist, before P3 adoption | COM-0007 | 1 | 1 / 1 / 1 / 1 | closed / completed |

All four cases passed:

- duplicate effect = 0
- false close = 0
- no guessing
- single Return adoption
- commit-chain integrity
- projection rebuild
- Authority boundary

Resolved integration finding: `SPEC_RUNTIME_ROOT` and `RUNNER_ROOT` were initially conflated. Phase 0 hash-only fallback masked that path-resolution defect. The strict resolver now anchors relative paths to the `RUNTIME_MANIFEST.md` parent and does not permit basename-only or hash-only fallback.

The full raw run tree remains in the preserved local Phase 1 PASS snapshot. This repository keeps proven summaries on `main` and avoids committing every generated runtime log by default.
