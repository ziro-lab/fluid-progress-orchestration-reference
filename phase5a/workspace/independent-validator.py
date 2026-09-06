"""Final validator fixture; parent runner records its deterministic result."""


def validate(result: dict[str, str]) -> bool:
    return result == {"title": "Alpha # tag", "mode": "safe"}
