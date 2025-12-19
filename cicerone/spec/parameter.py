"""Parameter model for OpenAPI parameters.

References:
- OpenAPI 3.x Parameter Object: https://spec.openapis.org/oas/v3.1.0#parameter-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import example as spec_example
from cicerone.spec import model_utils
from cicerone.spec import schema as spec_schema


class Parameter(pydantic.BaseModel):
    """Represents an OpenAPI parameter object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    name: str | None = None
    in_: str | None = pydantic.Field(None, alias="in")
    description: str | None = None
    required: bool = False
    schema_: spec_schema.Schema | None = pydantic.Field(None, alias="schema")
    # OpenAPI 3.x fields
    style: str | None = None
    explode: bool | None = None
    example: typing.Any | None = None
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Parameter:
        """Create a Parameter from a dictionary."""
        excluded = {
            "name",
            "in",
            "description",
            "required",
            "schema",
            "style",
            "explode",
            "example",
            "examples",
        }
        return cls(
            name=data.get("name"),
            **{"in": data.get("in")},
            description=data.get("description"),
            required=data.get("required", False),
            schema=model_utils.parse_nested_object(data, "schema", spec_schema.Schema.from_dict),
            style=data.get("style"),
            explode=data.get("explode"),
            example=data.get("example"),
            examples=model_utils.parse_collection(data, "examples", spec_example.Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
