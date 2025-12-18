"""Parameter model for OpenAPI parameters.

References:
- OpenAPI 3.x Parameter Object: https://spec.openapis.org/oas/v3.1.0#parameter-object
- Swagger 2.0 Parameter Object: https://swagger.io/specification/v2/#parameter-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.example import Example
from cicerone.spec.model_utils import parse_collection, parse_nested_object
from cicerone.spec.schema import Schema


class Parameter(BaseModel):
    """Represents an OpenAPI parameter object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    name: str | None = None
    in_: str | None = Field(None, alias="in")
    description: str | None = None
    required: bool = False
    schema_: Schema | None = Field(None, alias="schema")
    # Swagger 2.0 fields
    type: str | None = None
    # OpenAPI 3.x fields
    style: str | None = None
    explode: bool | None = None
    example: Any | None = None
    examples: dict[str, Example] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Parameter:
        """Create a Parameter from a dictionary."""
        excluded = {
            "name",
            "in",
            "description",
            "required",
            "schema",
            "type",
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
            schema=parse_nested_object(data, "schema", Schema.from_dict),
            type=data.get("type"),
            style=data.get("style"),
            explode=data.get("explode"),
            example=data.get("example"),
            examples=parse_collection(data, "examples", Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
