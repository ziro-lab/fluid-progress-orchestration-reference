"""Parse timezone-aware ISO-8601 timestamps across the supported profiles."""

from __future__ import annotations

from datetime import datetime


def parse_timestamp(value: str, runtime_version: tuple[int, int]) -> datetime:
    if runtime_version not in {(3, 10), (3, 11)}:
        raise ValueError(f"unsupported runtime profile: {runtime_version!r}")
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")

    # Python 3.10 does not accept the UTC ``Z`` designator. Normalizing it
    # for both profiles keeps the result independent of the host interpreter.
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone offset or UTC Z")
    return parsed
