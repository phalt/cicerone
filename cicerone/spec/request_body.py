"""RequestBody model for OpenAPI request bodies.

References:
- OpenAPI 3.x Request Body Object: https://spec.openapis.org/oas/v3.1.0#request-body-object
"""

from typing import Any

from pydantic import BaseModel, Field


class RequestBody(BaseModel):
    """Represents an OpenAPI request body object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, Any] = Field(default_factory=dict)
    required: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RequestBody":
        """Create a RequestBody from a dictionary."""
        return cls(**data)
