# ISO Compatibility Parser

Make this tool usable according to this README. It must parse ISO-8601 timestamps for both supported runtime profiles `(3, 10)` and `(3, 11)` and return timezone-aware `datetime` values.

The accepted input includes offsets and the UTC `Z` designator. The behavior of the host Python version is not enough to establish behavior for both supported profiles. When local evidence leaves that version boundary unresolved, use the supplied read-only official reference at `tools/official_datetime_reference.py`, and record the source URL and claim in the worker Return.

Do not add a new dependency. Invalid timestamps should raise `ValueError`; no guessed timezone or silent local-time conversion is allowed.
