"""Tag model for OpenAPI tag definitions.

References:
- OpenAPI 3.x Tag Object: https://spec.openapis.org/oas/v3.1.0#tag-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils


class ExternalDocumentation(pydantic.BaseModel):
    """Represents external documentation."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    url: str
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> ExternalDocumentation:
        """Create ExternalDocumentation from a dictionary."""
        excluded = {"url", "description"}
        return cls(
            url=data["url"],
            description=data.get("description"),
            **{k: v for k, v in data.items() if k not in excluded},
        )


class Tag(pydantic.BaseModel):
    """Represents an OpenAPI Tag object."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    name: str
    description: str | None = None
    external_docs: ExternalDocumentation | None = None

    def __str__(self) -> str:
        """Return a readable string representation of the tag."""
        parts = [f"name='{self.name}'"]
        if self.description:
            parts.append(f"desc='{model_utils.truncate_text(self.description, 30)}'")
        return f"<Tag: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Tag:
        """Create a Tag from a dictionary."""
        excluded = {"name", "description", "externalDocs"}
        return cls(
            name=data["name"],
            description=data.get("description"),
            external_docs=model_utils.parse_nested_object(data, "externalDocs", ExternalDocumentation.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
