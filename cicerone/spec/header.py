"""Header model for OpenAPI headers.

References:
- OpenAPI 3.x Header Object: https://spec.openapis.org/oas/v3.1.0#header-object
"""

from typing import Any

from pydantic import BaseModel, Field


class Header(BaseModel):
    """Represents an OpenAPI header object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    required: bool = False
    schema_: dict[str, Any] | None = Field(None, alias="schema")
    style: str | None = None
    explode: bool | None = None
    example: Any | None = None
    examples: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Header":
        """Create a Header from a dictionary."""
        return cls(**data)
