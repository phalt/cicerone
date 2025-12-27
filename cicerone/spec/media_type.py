"""MediaType model for OpenAPI media type objects.

References:
- OpenAPI 3.x Media Type Object: https://spec.openapis.org/oas/v3.1.0#media-type-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import encoding as spec_encoding
from cicerone.spec import example as spec_example
from cicerone.spec import model_utils


class MediaType(pydantic.BaseModel):
    """Represents an OpenAPI Media Type Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    schema_: dict[str, typing.Any] | None = pydantic.Field(None, alias="schema")
    example: typing.Any | None = None
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)
    encoding: dict[str, spec_encoding.Encoding] = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> MediaType:
        """Create a MediaType from a dictionary."""
        return cls(
            schema=data.get("schema"),
            example=data.get("example"),
            examples=model_utils.parse_collection(data, "examples", spec_example.Example.from_dict),
            encoding=model_utils.parse_collection(data, "encoding", spec_encoding.Encoding.from_dict),
            **{k: v for k, v in data.items() if k not in {"schema", "example", "examples", "encoding"}},
        )

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the MediaType to a dictionary representation.

        Returns:
            Dictionary representation of the media type
        """
        result: dict[str, typing.Any] = {}

        if self.schema_ is not None:
            result["schema"] = self.schema_

        if self.example is not None:
            result["example"] = self.example

        if self.examples:
            result["examples"] = {k: v.to_dict() for k, v in self.examples.items()}

        if self.encoding:
            result["encoding"] = {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.encoding.items()}

        # Handle extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:
                    result[key] = value

        return result
