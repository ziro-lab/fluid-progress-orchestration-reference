"""Initial bounded profile normalizer fixture. The first repair removes the inline-comment loss."""


def normalize_profile(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        content = line.split("#", 1)[0].strip()
        if "=" not in content:
            continue
        key, value = content.split("=", 1)
        result[key.strip()] = value.strip().strip('"')
    return result
