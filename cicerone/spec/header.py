"""Header model for OpenAPI headers.

References:
- OpenAPI 3.x Header Object: https://spec.openapis.org/oas/v3.1.0#header-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import Field

from cicerone.spec import example as example_module
from cicerone.spec import model_utils
from cicerone.spec import schema as schema_module

# Extract classes for type annotations
Example = example_module.Example
Schema = schema_module.Schema


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
        excluded = {"description", "required", "schema", "style", "explode", "example", "examples"}
        return cls(
            description=data.get("description"),
            required=data.get("required", False),
            schema=model_utils.parse_nested_object(data, "schema", schema_module.Schema.from_dict),
            style=data.get("style"),
            explode=data.get("explode"),
            example=data.get("example"),
            examples=model_utils.parse_collection(data, "examples", example_module.Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
