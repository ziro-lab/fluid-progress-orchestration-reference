# Task Runner

Make this small command-line tool usable according to this contract. The initial implementation is intentionally incomplete; discover the requirements from this README, the source, and the tests.

Run it with:

```text
python src/task_runner.py input.json output.json
```

The input is a JSON object with a `tasks` array. Each task has an `id`, an argv-style `command` array, and an optional positive `timeout_seconds`.

The output must contain one result per input task, in the same order:

- `success` only when the process exits with code `0` before the timeout.
- `failed` when the process exits with a non-zero code; preserve its exit code, stdout, and stderr.
- `timed_out` when the timeout expires; never report fake success, do not invent an exit code, and preserve any captured output that is available.
- `invalid` for malformed task records; continue processing the remaining tasks.

Commands are argv arrays and must not be interpreted by a shell. Output must be deterministic JSON: no timestamps, random identifiers, or environment-specific fields. The report itself should be generated with process exit code `0` even when an individual task is `failed` or `timed_out`.

Use the Python standard-library subprocess contract. If the behavior of `run`, `timeout`, or `TimeoutExpired` is not established by local evidence, use the supplied read-only official-reference capability at `tools/official_subprocess_reference.py` and retain the source URL and claim in your worker record.

Human preference is not part of this task. Do not modify files outside this bounded project.
