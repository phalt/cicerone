"""Response model for OpenAPI responses.

References:
- OpenAPI 3.x Response Object: https://spec.openapis.org/oas/v3.1.0#response-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.example import Example
from cicerone.spec.header import Header
from cicerone.spec.link import Link
from cicerone.spec.media_type import MediaType
from cicerone.spec.model_utils import parse_collection, parse_nested_object
from cicerone.spec.schema import Schema


class Response(BaseModel):
    """Represents an OpenAPI response object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, MediaType] = Field(default_factory=dict)
    headers: dict[str, Header] = Field(default_factory=dict)
    links: dict[str, Link] = Field(default_factory=dict)
    schema_: Schema | None = Field(None, alias="schema")
    examples: dict[str, Example] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        """Create a Response from a dictionary."""
        excluded = {"description", "schema", "content", "headers", "links", "examples"}
        return cls(
            description=data.get("description"),
            schema=parse_nested_object(data, "schema", Schema.from_dict),
            content=parse_collection(data, "content", MediaType.from_dict),
            headers=parse_collection(data, "headers", Header.from_dict),
            links=parse_collection(data, "links", Link.from_dict),
            examples=parse_collection(data, "examples", Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
