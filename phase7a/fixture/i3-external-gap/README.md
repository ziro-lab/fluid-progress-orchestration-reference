# I3 — Vendor Release Manifest

Make this bounded manifest builder usable according to the project contract.
Implement, validate, and confirm completion.

`build_manifest(config)` receives a mapping with `name`, `version`, `channel`,
and an `artifacts` list. It must produce a deterministic vendor manifest.

The local project does not contain the vendor's version-specific contract for
the channel field, the manifest schema version, or artifact ordering. Do not
guess those meanings from the function name or from a plausible local default.
If implementation reaches that external gap, return a structured blocker to
FPO. FPO owns any official read-only research and will persist source-bound
Evidence before implementation resumes.

No Human preference is part of this fixture. Do not modify files outside this
project.
