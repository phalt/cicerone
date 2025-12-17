"""MediaType model for OpenAPI media type objects.

References:
- OpenAPI 3.x Media Type Object: https://spec.openapis.org/oas/v3.1.0#media-type-object
"""

from typing import Any

from pydantic import BaseModel, Field


class MediaType(BaseModel):
    """Represents an OpenAPI Media Type Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    schema_: dict[str, Any] | None = Field(None, alias="schema")
    example: Any | None = None
    examples: dict[str, Any] = Field(default_factory=dict)
    encoding: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MediaType":
        """Create a MediaType from a dictionary."""
        return cls(**data)
