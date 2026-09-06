# Security Policy

Fluid Progress Orchestration (FPO) is an experimental control and reliability architecture. It is **not** a sandbox, a general security boundary, or a production-safety certification.

## Supported version

Security reports should target the current public `main` reference baseline unless a specific release or commit is named.

Historical phase fixtures and recorded evidence retain their documented proof scope; they do not imply that every host, provider, model, or integration is secure.

## What is useful to report

Examples of issues that are especially relevant to FPO include:

- untrusted Return or Artifact content mutating trusted Control State or Authority;
- stale or mismatched delegated work regaining Effect authority;
- approval, authorization, or capability-envelope bypass;
- blind retry after an Effect outcome becomes unknown;
- Settlement or fencing accepted without sufficient proof;
- resolver/path behavior escaping the intended Runtime Manifest boundary;
- a worker or capability being able to promote its own result into FPO Acceptance or Close;
- repository/runtime tooling that can unexpectedly expose credentials, private data, or persistent external Effects.

A model hallucination, jailbreak, or prompt-injection behavior is not automatically an FPO vulnerability by itself. It becomes relevant when the FPO runtime or integration incorrectly promotes untrusted behavior into trusted Authority, Evidence, Effect, Adoption, Acceptance, or Settlement.

## Reporting a vulnerability

If GitHub private vulnerability reporting is enabled for this repository, please use **Security → Report a vulnerability** so sensitive details are not posted publicly.

If that option is not available, open a minimal public Issue asking for a private reporting route. **Do not include credentials, exploit secrets, private prompts, personal data, or sensitive reproduction material in a public Issue.**

Please include, when practical:

- the FPO commit/release;
- the affected runtime/provider/integration;
- the violated boundary or invariant;
- the smallest safe reproduction;
- whether any persistent or external Effect occurred.

## Scope and warranty

FPO is distributed under the Apache License 2.0 on an **AS IS** basis. Recorded `Proven`, `PASS`, or similar claims apply only to the evidence scope stated by the relevant phase/report; they are not blanket guarantees for arbitrary environments.
