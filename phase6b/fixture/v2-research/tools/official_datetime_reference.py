"""Bounded read-only official-reference capability for the V2 fixture."""

from __future__ import annotations

import json


def main() -> int:
    print(json.dumps({
        "source_url": "https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat",
        "source_title": "Python datetime.datetime.fromisoformat documentation",
        "claims": [
            "The fromisoformat documentation records version-specific support for the UTC Z designator.",
            "A compatibility layer targeting an earlier supported profile must normalize Z before relying on the host parser.",
            "Offset-bearing values produce aware datetimes and should not be converted to an assumed local timezone.",
        ],
        "access": "read-only fixture capability",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
