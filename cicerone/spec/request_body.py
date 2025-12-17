"""RequestBody model for OpenAPI request bodies.

References:
- OpenAPI 3.x Request Body Object: https://spec.openapis.org/oas/v3.1.0#request-body-object
"""

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.media_type import MediaType


class RequestBody(BaseModel):
    """Represents an OpenAPI request body object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, MediaType] = Field(default_factory=dict)
    required: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RequestBody":
        """Create a RequestBody from a dictionary."""
        body_data: dict[str, Any] = {
            "description": data.get("description"),
            "required": data.get("required", False),
        }

        # Parse content as MediaType objects
        if "content" in data:
            body_data["content"] = {
                media_type: MediaType.from_dict(media_data)
                for media_type, media_data in data["content"].items()
            }

        # Add any extra fields
        for key, value in data.items():
            if key not in body_data:
                body_data[key] = value

        return cls(**body_data)

