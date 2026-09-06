"""Release badge implementation for the resolved channel presentation."""


def render_badge(channel, version):
    colors = {"stable": "green", "canary": "amber"}
    return {"text": f"{channel} {version}", "color": colors[channel]}
