"""RequestBody model for OpenAPI request bodies.

References:
- OpenAPI 3.x Request Body Object: https://spec.openapis.org/oas/v3.1.0#request-body-object
"""

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.media_type import MediaType
from cicerone.spec.model_utils import parse_collection


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
        return cls(
            description=data.get("description"),
            content=parse_collection(data, "content", MediaType.from_dict),
            required=data.get("required", False),
            **{k: v for k, v in data.items() if k not in {"description", "content", "required"}},
        )
