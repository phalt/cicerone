"""RequestBody model for OpenAPI request bodies.

References:
- OpenAPI 3.x Request Body Object: https://spec.openapis.org/oas/v3.1.0#request-body-object
"""

from typing import Any

from pydantic import BaseModel
from pydantic import Field

from cicerone.spec import media_type as media_type_module
from cicerone.spec import model_utils

# Extract classes for type annotations
MediaType = media_type_module.MediaType


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
            content=model_utils.parse_collection(data, "content", media_type_module.MediaType.from_dict),
            required=data.get("required", False),
            **{k: v for k, v in data.items() if k not in {"description", "content", "required"}},
        )
