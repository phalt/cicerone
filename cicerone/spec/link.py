"""Link model for OpenAPI links.

References:
- OpenAPI 3.x Link Object: https://spec.openapis.org/oas/v3.1.0#link-object
"""

from typing import Any

from pydantic import BaseModel, Field


class Link(BaseModel):
    """Represents an OpenAPI Link Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    operationRef: str | None = None
    operationId: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    requestBody: Any | None = None
    description: str | None = None
    server: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Link":
        """Create a Link from a dictionary."""
        # Simple passthrough - pydantic handles all fields with extra="allow"
        return cls(**data)
