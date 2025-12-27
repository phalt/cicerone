"""Header model for OpenAPI headers.

References:
- OpenAPI 3.x Header Object: https://spec.openapis.org/oas/v3.1.0#header-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import example as spec_example
from cicerone.spec import model_utils
from cicerone.spec import schema as spec_schema


class Header(pydantic.BaseModel):
    """Represents an OpenAPI header object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    required: bool = False
    schema_: spec_schema.Schema | None = pydantic.Field(None, alias="schema")
    style: str | None = None
    explode: bool | None = None
    example: typing.Any | None = None
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Header:
        """Create a Header from a dictionary."""
        excluded = {"description", "required", "schema", "style", "explode", "example", "examples"}
        return cls(
            description=data.get("description"),
            required=data.get("required", False),
            schema=model_utils.parse_nested_object(data, "schema", spec_schema.Schema.from_dict),
            style=data.get("style"),
            explode=data.get("explode"),
            example=data.get("example"),
            examples=model_utils.parse_collection(data, "examples", spec_example.Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the Header to a dictionary representation.

        Returns:
            Dictionary representation of the header
        """
        result: dict[str, typing.Any] = {}

        if self.description is not None:
            result["description"] = self.description

        # Always include required as it has a default
        result["required"] = self.required

        if self.schema_ is not None:
            result["schema"] = self.schema_.to_dict()

        if self.style is not None:
            result["style"] = self.style

        if self.explode is not None:
            result["explode"] = self.explode

        if self.example is not None:
            result["example"] = self.example

        if self.examples:
            result["examples"] = {k: v.to_dict() for k, v in self.examples.items()}

        # Handle extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:
                    result[key] = value

        return result
