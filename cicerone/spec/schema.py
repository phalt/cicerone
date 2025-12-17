"""Schema model for JSON Schema / OpenAPI Schema objects."""

from typing import Any, Mapping

from pydantic import BaseModel, Field


class Schema(BaseModel):
    """Represents a JSON Schema / OpenAPI Schema object."""

    model_config = {"extra": "allow"}

    title: str | None = None
    type: str | None = None
    description: str | None = None
    properties: dict[str, "Schema"] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    items: "Schema | None" = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Schema":
        """Create a Schema from a dictionary, handling nested schemas."""
        schema_data: dict[str, Any] = {
            "title": data.get("title"),
            "type": data.get("type"),
            "description": data.get("description"),
            "required": data.get("required", []),
        }

        # Handle nested properties
        if "properties" in data:
            schema_data["properties"] = {name: cls.from_dict(prop) for name, prop in data["properties"].items()}

        # Handle array items
        if "items" in data and isinstance(data["items"], dict):
            schema_data["items"] = cls.from_dict(data["items"])

        # Store any additional fields
        for key, value in data.items():
            if key not in schema_data:
                schema_data[key] = value

        return cls(**schema_data)
