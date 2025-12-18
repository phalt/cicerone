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
    """Represents a JSON Schema / OpenAPI Schema object."""

    # Allow extra fields to support full JSON Schema vocabulary and vendor extensions
    model_config = {"extra": "allow"}

    title: str | None = None
    type: str | None = None
    description: str | None = None
    properties: dict[str, Schema] = pydantic.Field(default_factory=dict)
    required: list[str] = pydantic.Field(default_factory=list)
    items: Schema | None = None
    # Composition keywords
    all_of: "list[Schema] | None" = pydantic.Field(None, alias="allOf")
    one_of: "list[Schema] | None" = pydantic.Field(None, alias="oneOf")
    any_of: "list[Schema] | None" = pydantic.Field(None, alias="anyOf")
    not_: "Schema | None" = pydantic.Field(None, alias="not")

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

        # Helper to parse list of schemas
        def parse_schema_list(field_name: str) -> list[Schema] | None:
            if field_name in data and isinstance(data[field_name], list):
                return [cls.from_dict(item) for item in data[field_name] if isinstance(item, dict)]
            return None

        return cls(
            title=data.get("title"),
            type=data.get("type"),
            description=data.get("description"),
            required=data.get("required", []),
            properties=model_utils.parse_collection(data, "properties", cls.from_dict),
            items=model_utils.parse_nested_object(data, "items", cls.from_dict),
            allOf=parse_schema_list("allOf"),
            oneOf=parse_schema_list("oneOf"),
            anyOf=parse_schema_list("anyOf"),
            # Use dict unpacking for 'not' since it's a Python keyword
            **{"not": model_utils.parse_nested_object(data, "not", cls.from_dict)} if "not" in data else {},
            **{k: v for k, v in data.items() if k not in excluded},
        )
