# Report Normalizer

Make this bounded report utility usable according to these materials.

Requirements:
- `normalize_label(value)` returns lowercase hyphen-separated words and removes punctuation.
- `sort_versions(values)` orders simple `major.minor.patch` versions numerically.
- `build_report(records)` emits one stable `label: version` line per record.
- Keep the implementation local, deterministic, and dependency-free.
