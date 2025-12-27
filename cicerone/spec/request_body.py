"""RequestBody model for OpenAPI request bodies.

References:
- OpenAPI 3.x Request Body Object: https://spec.openapis.org/oas/v3.1.0#request-body-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import media_type as spec_media_type
from cicerone.spec import model_utils


class RequestBody(pydantic.BaseModel):
    """Represents an OpenAPI request body object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, spec_media_type.MediaType] = pydantic.Field(default_factory=dict)
    required: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "RequestBody":
        """Create a RequestBody from a dictionary."""
        return cls(
            description=data.get("description"),
            content=model_utils.parse_collection(data, "content", spec_media_type.MediaType.from_dict),
            required=data.get("required", False),
            **{k: v for k, v in data.items() if k not in {"description", "content", "required"}},
        )

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the RequestBody to a dictionary representation.

        This method converts the RequestBody object back to a dict format that matches
        the original OpenAPI specification.

        Returns:
            Dictionary representation of the request body
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
                    # MediaType stores schema as dict, so just use it as-is
                    result["content"][media_type] = {
                        "schema": media_type_obj.schema_,
                        **({"example": media_type_obj.example} if media_type_obj.example is not None else {}),
                    }

        # Always include required field as it has a default
        result["required"] = self.required

        # Handle extra fields
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:
                    result[key] = value

        return result
