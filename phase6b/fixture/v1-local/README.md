# Local Ledger

Make this small tool usable according to this README. Read the source and tests, determine the current state, and make the smallest safe change within this project.

`src/ledger.py` exposes `summarize(records)`. Each input record has an `id` and a decimal `amount` string. The result must:

- preserve accepted records in input order;
- reject missing IDs and negative or malformed amounts without aborting the whole report;
- calculate the exact decimal total and serialize it with two fractional digits;
- remain deterministic and contain no timestamps, random IDs, or environment data.

This is a local-only task. The README, source, and tests are sufficient; do not perform external research merely because it is available.
