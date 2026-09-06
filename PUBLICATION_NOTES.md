# Publication Notes

This repository is a **clean public reference snapshot** of Fluid Progress Orchestration (FPO).

## Development history

The Git history, experimental branches, pull requests, and other development-repository history are intentionally **not imported** here. The public repository starts from a new root commit so development-only metadata is not treated as part of the public API or proof surface.

## Public-copy redaction

Before publication, environment-specific local Windows user-home roots found in historical recorded evidence were normalized from the original local path to:

```text
C:\Users\<user>
```

A total of **31 path occurrences** were normalized in the public snapshot.

No FPO Core, current Spec, Runtime Manifest, Authority contract, or current runtime semantics were changed by this publication redaction.

Because this normalization changes bytes, the affected public historical evidence files are **not byte-identical copies** of their private development-source originals. Treat them as public recorded evidence/documentation with their existing narrow proof scope, not as hash-identical archival originals.

The private development source retains the original evidence bytes.

## Privacy scan

The sanitized snapshot was checked before import for obvious publication hazards including:

- environment-specific Windows/macOS/Linux user-home roots;
- common personal webmail addresses;
- GitHub personal access token patterns;
- OpenAI-style secret-key patterns;
- AWS access-key patterns;
- private-key blocks.

The public import was allowed only after those checks passed.

## Evidence scope

`Proven`, `PASS`, `Recorded`, `Candidate`, and similar terms retain only the scope stated by their corresponding reports. Publication does not widen those claims.
