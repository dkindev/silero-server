"""Package initialization."""

from importlib.metadata import metadata

__metadata__ = metadata("silero-server")

__project_urls__ = {}
for item in __metadata__.get_all("Project-URL") or []:
    label, url = item.split(",", 1)
    __project_urls__[label.strip()] = url.strip()

__all__ = ["__metadata__", "__project_urls__"]
