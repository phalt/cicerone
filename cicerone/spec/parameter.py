"""Parameter model for OpenAPI parameters.

References:
- OpenAPI 3.x Parameter Object: https://spec.openapis.org/oas/v3.1.0#parameter-object
- Swagger 2.0 Parameter Object: https://swagger.io/specification/v2/#parameter-object
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from cicerone.spec.schema import Schema


class Parameter(BaseModel):
    """Represents an OpenAPI parameter object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    name: str | None = None
    in_: str | None = Field(None, alias="in")
    description: str | None = None
    required: bool = False
    schema_: "Schema | None" = Field(None, alias="schema")
    # Swagger 2.0 fields
    type: str | None = None
    # OpenAPI 3.x fields
    style: str | None = None
    explode: bool | None = None
    example: Any | None = None
    examples: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Parameter":
        """Create a Parameter from a dictionary."""
        from cicerone.spec.schema import Schema

        param_data: dict[str, Any] = {
            "name": data.get("name"),
            "in": data.get("in"),
            "description": data.get("description"),
            "required": data.get("required", False),
            "type": data.get("type"),
            "style": data.get("style"),
            "explode": data.get("explode"),
            "example": data.get("example"),
            "examples": data.get("examples", {}),
        }

        # Parse schema as Schema object
        if "schema" in data:
            param_data["schema"] = Schema.from_dict(data["schema"])

        # Add any extra fields
        for key, value in data.items():
            if key not in param_data:
                param_data[key] = value

        return cls(**param_data)

