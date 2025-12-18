"""MediaType model for OpenAPI media type objects.

References:
- OpenAPI 3.x Media Type Object: https://spec.openapis.org/oas/v3.1.0#media-type-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.encoding import Encoding
from cicerone.spec.example import Example


class MediaType(BaseModel):
    """Represents an OpenAPI Media Type Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    schema_: dict[str, Any] | None = Field(None, alias="schema")
    example: Any | None = None
    examples: dict[str, Example] = Field(default_factory=dict)
    encoding: dict[str, Encoding] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MediaType:
        """Create a MediaType from a dictionary."""
        media_type_data: dict[str, Any] = {
            "schema": data.get("schema"),
            "example": data.get("example"),
        }

        # Parse examples as Example objects
        if "examples" in data:
            media_type_data["examples"] = {
                name: Example.from_dict(example_data)
                for name, example_data in data["examples"].items()
            }

        # Parse encoding as Encoding objects
        if "encoding" in data:
            media_type_data["encoding"] = {
                name: Encoding.from_dict(encoding_data)
                for name, encoding_data in data["encoding"].items()
            }

        # Add any extra fields
        for key, value in data.items():
            if key not in media_type_data:
                media_type_data[key] = value

        return cls(**media_type_data)
