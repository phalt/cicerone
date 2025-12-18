"""Response model for OpenAPI responses.

References:
- OpenAPI 3.x Response Object: https://spec.openapis.org/oas/v3.1.0#response-object
- Swagger 2.0 Response Object: https://swagger.io/specification/v2/#response-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.example import Example
from cicerone.spec.header import Header
from cicerone.spec.link import Link
from cicerone.spec.media_type import MediaType
from cicerone.spec.schema import Schema


class Response(BaseModel):
    """Represents an OpenAPI response object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, MediaType] = Field(default_factory=dict)
    headers: dict[str, Header] = Field(default_factory=dict)
    links: dict[str, Link] = Field(default_factory=dict)
    # Swagger 2.0 fields
    schema_: Schema | None = Field(None, alias="schema")
    examples: dict[str, Example] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        """Create a Response from a dictionary."""
        from cicerone.spec.schema import Schema

        response_data: dict[str, Any] = {
            "description": data.get("description"),
        }

        # Parse schema as Schema object (Swagger 2.0)
        if "schema" in data:
            response_data["schema"] = Schema.from_dict(data["schema"])

        # Parse content as MediaType objects
        if "content" in data:
            response_data["content"] = {
                media_type: MediaType.from_dict(media_data)
                for media_type, media_data in data["content"].items()
            }

        # Parse headers as Header objects
        if "headers" in data:
            response_data["headers"] = {
                header_name: Header.from_dict(header_data)
                for header_name, header_data in data["headers"].items()
            }

        # Parse links as Link objects
        if "links" in data:
            response_data["links"] = {
                link_name: Link.from_dict(link_data)
                for link_name, link_data in data["links"].items()
            }

        # Parse examples as Example objects
        if "examples" in data:
            response_data["examples"] = {
                name: Example.from_dict(example_data)
                for name, example_data in data["examples"].items()
            }

        # Add any extra fields
        for key, value in data.items():
            if key not in response_data:
                response_data[key] = value

        return cls(**response_data)
