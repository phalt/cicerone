"""RequestBody model for OpenAPI request bodies.

References:
- OpenAPI 3.x Request Body Object: https://spec.openapis.org/oas/v3.1.0#request-body-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import media_type as spec_media_type
from cicerone.spec import model_utils


class RequestBody(pydantic.BaseModel):
    """Represents an OpenAPI request body object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, spec_media_type.MediaType] = pydantic.Field(default_factory=dict)
    required: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "RequestBody":
        """Create a RequestBody from a dictionary."""
        return cls(
            description=data.get("description"),
            content=model_utils.parse_collection(data, "content", spec_media_type.MediaType.from_dict),
            required=data.get("required", False),
            **{k: v for k, v in data.items() if k not in {"description", "content", "required"}},
        )
