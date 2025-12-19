"""Encoding model for OpenAPI encoding objects.

References:
- OpenAPI 3.x Encoding Object: https://spec.openapis.org/oas/v3.1.0#encoding-object
"""

from __future__ import annotations

import typing

import pydantic


class Encoding(pydantic.BaseModel):
    """Represents an OpenAPI Encoding Object.

    An encoding definition applied to a single schema property.
    """

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    contentType: str | None = None
    headers: dict[str, typing.Any] = pydantic.Field(default_factory=dict)  # Header objects
    style: str | None = None
    explode: bool = False
    allowReserved: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Encoding:
        """Create an Encoding from a dictionary."""
        # Simple passthrough - pydantic handles all fields with extra="allow"
        return cls(**data)
