"""Small deterministic label slugger used by the Phase 7A I1 fixture."""

import re


def build_slugs(labels):
    accepted = []
    rejected = []
    for index, raw in enumerate(labels):
        if not isinstance(raw, str):
            rejected.append({"index": index, "reason": "not a string"})
            continue
        trimmed = raw.strip()
        if not trimmed:
            rejected.append({"index": index, "reason": "empty label"})
            continue
        slug = re.sub(r"[^A-Za-z0-9]+", "-", trimmed.lower()).strip("-")
        accepted.append({"input": trimmed, "slug": slug})
    return {"accepted": accepted, "rejected": rejected}
