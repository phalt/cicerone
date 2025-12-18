"""Header model for OpenAPI headers.

References:
- OpenAPI 3.x Header Object: https://spec.openapis.org/oas/v3.1.0#header-object
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
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
    examples: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Header:
        """Create a Header from a dictionary."""
        from cicerone.spec.schema import Schema

        header_data: dict[str, Any] = {
            "description": data.get("description"),
            "required": data.get("required", False),
            "style": data.get("style"),
            "explode": data.get("explode"),
            "example": data.get("example"),
            "examples": data.get("examples", {}),
        }

        # Parse schema as Schema object
        if "schema" in data:
            header_data["schema"] = Schema.from_dict(data["schema"])

        # Add any extra fields
        for key, value in data.items():
            if key not in header_data:
                header_data[key] = value

        return cls(**header_data)

