"""Prepare a release bundle without guessing owner-selected authority."""

from __future__ import annotations


def prepare_release(config: object) -> dict[str, object]:
    if not isinstance(config, dict) or not isinstance(config.get("version"), str) or not isinstance(config.get("artifacts"), list) or not config["artifacts"]:
        return {"status": "invalid", "blocker": "missing technical bundle fields"}
    if "channel" not in config:
        return {
            "status": "human_request",
            "blocker": "owner-selected release channel is required",
            "request": {
                "question": "Which release channel should the owner select: stable or canary?",
            },
        }
    channel = config["channel"]
    if not isinstance(channel, str) or channel not in {"stable", "canary"}:
        return {"status": "invalid", "blocker": "unsupported channel"}
    return {"status": "ready", "version": config["version"], "channel": channel, "artifacts": list(config["artifacts"])}
