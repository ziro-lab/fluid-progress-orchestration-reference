"""Parent-only read-only snapshot of the vendor's official contract."""

SOURCE_URL = "https://vendor.example.invalid/release-manifest/v2"


def read_official_contract():
    return {
        "source_url": SOURCE_URL,
        "claim": "Manifest schema v2 uses track for the release channel, preserves artifact order, and accepts stable or canary.",
        "schema_version": 2,
        "channel_field": "track",
        "allowed_tracks": ["stable", "canary"],
        "artifact_order": "preserve-input-order",
        "read_only": True,
    }
