# 04 — Operational Policies v0.1.4.2

Status: **NON-SAFETY OPERATIONAL POLICY**

These policies are intentionally outside Parallel Safety conformance.

# A. Model Policy

Recommended baseline:

- Sol High — FPO material judgment
- Sol Medium — Flow Mini Planning / Execution supervision
- Luna xhigh — standard workforce
- Luna-first for safe/reversible/local evidence-producing attempts
- Terra — no standard route

# B. Provider-local Recovery Routing

Recovery under delegated execution:

```text
FAIL / NO_PROGRESS / BLOCKED
→ reconcile current reality
→ classify blocker
```

Routes:

- evidence/observation missing or stale → acquire/revalidate,
- authority/approval gap → FPO owner,
- tool/capability gap → bind capability,
- wrong Problem Form → Fresh by default,
- valid Form + new approach → Luna xhigh,
- reasoning capacity gap → stronger Luna / Sol,
- unresolved Effect/mutator → existing FPO/Provider reconcile,
- material upper-layer ambiguity → FPO/Sol judgment.

This policy does not replace P5 or redefine compensation/Acceptance.

# C. Parallel Efficiency Policy

Safety says whether concurrency is allowed, not whether it is optimal.

Efficiency policy may decide:

- 1/2/3 active workers,
- expected marginal value,
- hedge timing,
- throughput/token/latency trade-offs,
- low-value slot preemption,
- model choice for cost/quality.

`host_parallel_cap = 3` belongs here/Host Policy.

Benchmark results do not change Safety verdict unless they expose a correctness/liveness violation.

Correctness-relevant hard capacity remains Provider Safety admission, not Benchmark-only policy.
