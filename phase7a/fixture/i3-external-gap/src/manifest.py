"""Build the vendor release manifest defined by the persisted I3 Evidence."""


SCHEMA_VERSION = 2
ALLOWED_TRACKS = {"stable", "canary"}


def build_manifest(config):
    """Return a deterministic schema-v2 manifest for ``config``.

    The persisted source-bound Evidence defines ``track`` as the channel
    field, permits the stable and canary tracks, and requires artifact order
    to be preserved.
    """
    channel = config["channel"]
    if not isinstance(channel, str) or channel not in ALLOWED_TRACKS:
        raise ValueError("channel must be 'stable' or 'canary'")

    return {
        "schema_version": SCHEMA_VERSION,
        "name": config["name"],
        "version": config["version"],
        "track": channel,
        "artifacts": list(config["artifacts"]),
    }
