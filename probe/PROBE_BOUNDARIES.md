# Probe Boundaries

## Included

- local filesystem only
- one finite work
- one deterministic delegated Capability
- immutable records
- semantic commit + CAS
- projection rebuild
- operation query/cancel/reconcile abstraction
- fault injection

## Excluded

- multi-work / parallel scheduler
- real Web research
- GUI automation
- public deployment
- credentials / API keys
- irreversible external Effect
- assetization
- non-software domain
- production data

Probe の失敗を理由に Core を先に増築しない。まず Contract / Schema / Projection / Runner mechanism のどこが破れたかを特定する。
