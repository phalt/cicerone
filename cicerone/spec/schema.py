"""Schema model for JSON Schema / OpenAPI Schema objects.

References:
- OpenAPI 3.x Schema Object: https://spec.openapis.org/oas/v3.1.0#schema-object
- JSON Schema: https://json-schema.org/specification
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils


class Schema(pydantic.BaseModel):
    """Represents a JSON Schema / OpenAPI Schema object.

    This model supports the full JSON Schema and OpenAPI Schema vocabulary, including:
    - Standard fields: type, properties, required, items, title, description
    - Composition keywords: allOf, oneOf, anyOf, not
    - Extra fields via Pydantic's extra="allow" for: $ref, enum, format, nullable,
      default, example, and vendor extensions (x-*)

    Use from_dict() to parse a schema dictionary and to_dict() to convert back to dict.
    """

    # Allow extra fields to support full JSON Schema vocabulary and vendor extensions
    model_config = {"extra": "allow"}

    title: str | None = None
    type: str | list[str] | None = None
    description: str | None = None
    properties: dict[str, Schema] = pydantic.Field(default_factory=dict)
    required: list[str] = pydantic.Field(default_factory=list)
    items: Schema | None = None
    # Composition keywords
    all_of: list[Schema] | None = pydantic.Field(None, alias="allOf")
    one_of: list[Schema] | None = pydantic.Field(None, alias="oneOf")
    any_of: list[Schema] | None = pydantic.Field(None, alias="anyOf")
    not_: Schema | None = pydantic.Field(None, alias="not")

    def __str__(self) -> str:
        """Return a readable string representation of the schema."""
        parts = []
        if self.title:
            parts.append(f"'{self.title}'")
        if self.type:
            parts.append(f"type={self.type}")
        if self.properties:
            parts.append(f"{len(self.properties)} properties")
        if self.required:
            parts.append(f"required={self.required}")
        if self.items:
            parts.append(f"items={self.items.type or 'object'}")

        content = ", ".join(parts) if parts else "empty schema"
        return f"<Schema: {content}>"

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Schema:
        """Create a Schema from a dictionary, handling nested schemas."""
        excluded = {
            "title",
            "type",
            "description",
            "required",
            "properties",
            "items",
            "allOf",
            "oneOf",
            "anyOf",
            "not",
        }

        return cls(
            title=data.get("title"),
            type=data.get("type"),
            description=data.get("description"),
            required=data.get("required", []),
            properties=model_utils.parse_collection(data, "properties", cls.from_dict),
            items=model_utils.parse_nested_object(data, "items", cls.from_dict),
            allOf=model_utils.parse_list_or_none(data, "allOf", cls.from_dict),
            oneOf=model_utils.parse_list_or_none(data, "oneOf", cls.from_dict),
            anyOf=model_utils.parse_list_or_none(data, "anyOf", cls.from_dict),
            # Use dict unpacking for 'not' since it's a Python keyword
            **{"not": model_utils.parse_nested_object(data, "not", cls.from_dict)} if "not" in data else {},
            **{k: v for k, v in data.items() if k not in excluded},
        )

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert the Schema to a dictionary representation.

        This method converts the Schema object back to a dict format that matches
        the original OpenAPI/JSON Schema specification. It handles nested schemas,
        composition keywords (allOf, oneOf, anyOf), and Pydantic extra fields like
        $ref, enum, format, and nullable.

        Returns:
            Dictionary representation of the schema
        """
        result: dict[str, typing.Any] = {}

        # Handle $ref - when present, return early as other fields are not relevant per JSON Schema spec
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__ and "$ref" in self.__pydantic_extra__:
            result["$ref"] = self.__pydantic_extra__["$ref"]
            return result

        # Handle standard fields
        if self.title is not None:
            result["title"] = self.title

        if self.type is not None:
            result["type"] = self.type

        if self.description is not None:
            result["description"] = self.description

        if self.properties:
            result["properties"] = {k: v.to_dict() for k, v in self.properties.items()}

        if self.required:
            result["required"] = self.required

        if self.items is not None:
            result["items"] = self.items.to_dict()

        # Handle composition keywords
        if self.all_of is not None:
            result["allOf"] = [s.to_dict() for s in self.all_of]

        if self.one_of is not None:
            result["oneOf"] = [s.to_dict() for s in self.one_of]

        if self.any_of is not None:
            result["anyOf"] = [s.to_dict() for s in self.any_of]

        if self.not_ is not None:
            result["not"] = self.not_.to_dict()

        # Handle extra fields (format, enum, nullable, etc.)
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for key, value in self.__pydantic_extra__.items():
                if key not in result:  # Don't override already set fields
                    result[key] = value

        return result
