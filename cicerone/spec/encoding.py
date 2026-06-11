"""Encoding model for OpenAPI encoding objects.

References:
- OpenAPI 3.x Encoding Object: https://spec.openapis.org/oas/v3.1.0#encoding-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import header as spec_header
from cicerone.spec import model_utils


class Encoding(pydantic.BaseModel):
    """Represents an OpenAPI Encoding Object.

    An encoding definition applied to a single schema property.
    """

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow", "populate_by_name": True}

    contentType: str | None = None
    headers: dict[str, spec_header.Header] = pydantic.Field(default_factory=dict)
    style: str | None = None
    explode: bool = False
    allowReserved: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Encoding:
        """Create an Encoding from a dictionary."""
        return cls(
            headers=model_utils.parse_collection(data, "headers", spec_header.Header.from_dict),
            **{k: v for k, v in data.items() if k != "headers"},
        )
