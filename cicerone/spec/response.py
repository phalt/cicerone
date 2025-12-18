"""Response model for OpenAPI responses.

References:
- OpenAPI 3.x Response Object: https://spec.openapis.org/oas/v3.1.0#response-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import example
from cicerone.spec import header
from cicerone.spec import link
from cicerone.spec import media_type
from cicerone.spec import model_utils


class Response(pydantic.BaseModel):
    """Represents an OpenAPI response object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: "dict[str, media_type.MediaType]" = pydantic.Field(default_factory=dict)
    headers: "dict[str, header.Header]" = pydantic.Field(default_factory=dict)
    links: "dict[str, link.Link]" = pydantic.Field(default_factory=dict)
    examples: "dict[str, example.Example]" = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Response:
        """Create a Response from a dictionary."""
        excluded = {"description", "content", "headers", "links", "examples"}
        return cls(
            description=data.get("description"),
            content=model_utils.parse_collection(data, "content", media_type.MediaType.from_dict),
            headers=model_utils.parse_collection(data, "headers", header.Header.from_dict),
            links=model_utils.parse_collection(data, "links", link.Link.from_dict),
            examples=model_utils.parse_collection(data, "examples", example.Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
