"""Link model for OpenAPI links.

References:
- OpenAPI 3.x Link Object: https://spec.openapis.org/oas/v3.1.0#link-object
"""

import typing

import pydantic


class Link(pydantic.BaseModel):
    """Represents an OpenAPI Link Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    operationRef: str | None = None
    operationId: str | None = None
    parameters: dict[str, typing.Any] = pydantic.Field(default_factory=dict)
    requestBody: typing.Any | None = None
    description: str | None = None
    server: dict[str, typing.Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "Link":
        """Create a Link from a dictionary."""
        # Simple passthrough - pydantic handles all fields with extra="allow"
        return cls(**data)

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the Link to a dictionary representation.

        Returns:
            Dictionary representation of the link
        """
        result: dict[str, typing.Any] = {}

        if self.operationRef is not None:
            result["operationRef"] = self.operationRef

        if self.operationId is not None:
            result["operationId"] = self.operationId

        if self.parameters:
            result["parameters"] = self.parameters

        if self.requestBody is not None:
            result["requestBody"] = self.requestBody

        if self.description is not None:
            result["description"] = self.description

        if self.server is not None:
            result["server"] = self.server

        # Handle extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:
                    result[key] = value

        return result
