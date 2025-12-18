"""Header model for OpenAPI headers.

References:
- OpenAPI 3.x Header Object: https://spec.openapis.org/oas/v3.1.0#header-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.example import Example
from cicerone.spec.schema import Schema


class Header(BaseModel):
    """Represents an OpenAPI header object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    required: bool = False
    schema_: Schema | None = Field(None, alias="schema")
    style: str | None = None
    explode: bool | None = None
    example: Any | None = None
    examples: dict[str, Example] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Header:
        """Create a Header from a dictionary."""
        from cicerone.spec.model_utils import parse_collection, parse_nested_object

        excluded = {"description", "required", "schema", "style", "explode", "example", "examples"}
        return cls(
            description=data.get("description"),
            required=data.get("required", False),
            schema=parse_nested_object(data, "schema", Schema.from_dict),
            style=data.get("style"),
            explode=data.get("explode"),
            example=data.get("example"),
            examples=parse_collection(data, "examples", Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
