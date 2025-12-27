"""Encoding model for OpenAPI encoding objects.

References:
- OpenAPI 3.x Encoding Object: https://spec.openapis.org/oas/v3.1.0#encoding-object
"""

from __future__ import annotations

import typing

import pydantic


class Encoding(pydantic.BaseModel):
    """Represents an OpenAPI Encoding Object.

    An encoding definition applied to a single schema property.
    """

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    contentType: str | None = None
    headers: dict[str, typing.Any] = pydantic.Field(default_factory=dict)  # Header objects
    style: str | None = None
    explode: bool = False
    allowReserved: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Encoding:
        """Create an Encoding from a dictionary."""
        # Simple passthrough - pydantic handles all fields with extra="allow"
        return cls(**data)

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the Encoding to a dictionary representation.

        Returns:
            Dictionary representation of the encoding
        """
        result: dict[str, typing.Any] = {}

        if self.contentType is not None:
            result["contentType"] = self.contentType

        if self.headers:
            result["headers"] = self.headers

        if self.style is not None:
            result["style"] = self.style

        # Always include explode and allowReserved as they have defaults
        result["explode"] = self.explode
        result["allowReserved"] = self.allowReserved

        # Handle extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:
                    result[key] = value

        return result
