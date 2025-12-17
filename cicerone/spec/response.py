"""Response model for OpenAPI responses.

References:
- OpenAPI 3.x Response Object: https://spec.openapis.org/oas/v3.1.0#response-object
- Swagger 2.0 Response Object: https://swagger.io/specification/v2/#response-object
"""

from typing import Any

from pydantic import BaseModel, Field


class Response(BaseModel):
    """Represents an OpenAPI response object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, Any] = Field(default_factory=dict)
    links: dict[str, Any] = Field(default_factory=dict)
    # Swagger 2.0 fields
    schema_: dict[str, Any] | None = Field(None, alias="schema")
    examples: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Response":
        """Create a Response from a dictionary."""
        return cls(**data)
