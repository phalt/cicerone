"""Schema model for JSON Schema / OpenAPI Schema objects.

References:
- OpenAPI 3.x Schema Object: https://spec.openapis.org/oas/v3.1.0#schema-object
- JSON Schema: https://json-schema.org/specification
"""

from typing import Any, Mapping

from pydantic import BaseModel, Field

from cicerone.spec.model_utils import parse_collection, parse_nested_object


class Schema(BaseModel):
    """Represents a JSON Schema / OpenAPI Schema object."""

    # Allow extra fields to support full JSON Schema vocabulary and vendor extensions
    model_config = {"extra": "allow"}

    title: str | None = None
    type: str | None = None
    description: str | None = None
    properties: dict[str, "Schema"] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    items: "Schema | None" = None

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
    def from_dict(cls, data: Mapping[str, Any]) -> "Schema":
        """Create a Schema from a dictionary, handling nested schemas."""
        excluded = {"title", "type", "description", "required", "properties", "items"}
        return cls(
            title=data.get("title"),
            type=data.get("type"),
            description=data.get("description"),
            required=data.get("required", []),
            properties=parse_collection(data, "properties", cls.from_dict),
            items=parse_nested_object(data, "items", cls.from_dict) if isinstance(data.get("items"), dict) else None,
            **{k: v for k, v in data.items() if k not in excluded},
        )
