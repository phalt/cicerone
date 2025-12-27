"""Response model for OpenAPI responses.

References:
- OpenAPI 3.x Response Object: https://spec.openapis.org/oas/v3.1.0#response-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import example as spec_example
from cicerone.spec import header as spec_header
from cicerone.spec import link as spec_link
from cicerone.spec import media_type as spec_media_type
from cicerone.spec import model_utils


class Response(pydantic.BaseModel):
    """Represents an OpenAPI response object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, spec_media_type.MediaType] = pydantic.Field(default_factory=dict)
    headers: dict[str, spec_header.Header] = pydantic.Field(default_factory=dict)
    links: dict[str, spec_link.Link] = pydantic.Field(default_factory=dict)
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Response:
        """Create a Response from a dictionary."""
        excluded = {"description", "content", "headers", "links", "examples"}
        return cls(
            description=data.get("description"),
            content=model_utils.parse_collection(data, "content", spec_media_type.MediaType.from_dict),
            headers=model_utils.parse_collection(data, "headers", spec_header.Header.from_dict),
            links=model_utils.parse_collection(data, "links", spec_link.Link.from_dict),
            examples=model_utils.parse_collection(data, "examples", spec_example.Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the Response to a dictionary representation.

        This method converts the Response object back to a dict format that matches
        the original OpenAPI specification.

        Returns:
            Dictionary representation of the response
        """
        result: dict[str, typing.Any] = {}

        # Handle $ref from extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__ and "$ref" in self.__pydantic_extra__:
            result["$ref"] = self.__pydantic_extra__["$ref"]
            return result

        if self.description is not None:
            result["description"] = self.description

        if self.content:
            result["content"] = {}
            for media_type, media_type_obj in self.content.items():
                if hasattr(media_type_obj, "to_dict"):
                    result["content"][media_type] = media_type_obj.to_dict()
                else:
                    # MediaType stores schema as dict
                    result["content"][media_type] = {
                        "schema": media_type_obj.schema_,
                        **({"example": media_type_obj.example} if media_type_obj.example is not None else {}),
                    }

        if self.headers:
            result["headers"] = {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.headers.items()}

        if self.links:
            result["links"] = {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.links.items()}

        if self.examples:
            result["examples"] = {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.examples.items()}

        # Handle extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:
                    result[key] = value

        return result
