"""Example model for OpenAPI examples.

References:
- OpenAPI 3.x Example Object: https://spec.openapis.org/oas/v3.1.0#example-object
"""

import typing

import pydantic


class Example(pydantic.BaseModel):
    """Represents an OpenAPI example object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    summary: str | None = None
    description: str | None = None
    value: typing.Any | None = None
    externalValue: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "Example":
        """Create an Example from a dictionary."""
        # Simple passthrough - pydantic handles all fields with extra="allow"
        return cls(**data)
