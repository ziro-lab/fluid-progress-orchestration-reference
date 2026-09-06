"""Bounded read-only official-reference capability for the naturalistic fixture.

This is a source-bound snapshot pointer, not a hidden oracle. It supplies only
the documented subprocess semantics needed to interpret a timeout result.
"""

from __future__ import annotations

import json


def main() -> int:
    print(json.dumps({
        "source_url": "https://docs.python.org/3/library/subprocess.html#subprocess.run",
        "source_title": "Python subprocess.run documentation",
        "claims": [
            "The timeout argument is passed to Popen.communicate; TimeoutExpired is raised when the timeout expires.",
            "TimeoutExpired output and stderr attributes may be bytes when captured, so a text-facing report must normalize them before serialization.",
            "The subprocess API does not treat a command argv list as shell syntax when shell is false.",
        ],
        "access": "read-only fixture capability",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
