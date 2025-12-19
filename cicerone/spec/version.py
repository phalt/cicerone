"""Version representation for OpenAPI specs.

References:
- OpenAPI 3.x Info Object (version field): https://spec.openapis.org/oas/v3.1.0#info-object
"""

from __future__ import annotations


class Version:
    """Simple version representation for OpenAPI specs."""

    def __init__(self, version_string: str):
        self.raw = version_string
        parts = version_string.split(".")
        self.major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
        self.minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        self.patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

    def __str__(self) -> str:
        return self.raw

    def __repr__(self) -> str:
        return f"Version('{self.raw}')"
