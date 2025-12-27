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

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the Example to a dictionary representation.

        Returns:
            Dictionary representation of the example
        """
        result: dict[str, typing.Any] = {}

        if self.summary is not None:
            result["summary"] = self.summary

        if self.description is not None:
            result["description"] = self.description

        if self.value is not None:
            result["value"] = self.value

        if self.externalValue is not None:
            result["externalValue"] = self.externalValue

        # Handle extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:
                    result[key] = value

        return result
