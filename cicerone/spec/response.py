"""Response model for OpenAPI responses.

References:
- OpenAPI 3.x Response Object: https://spec.openapis.org/oas/v3.1.0#response-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import Field

from cicerone.spec import example as example_module
from cicerone.spec import header as header_module
from cicerone.spec import link as link_module
from cicerone.spec import media_type as media_type_module
from cicerone.spec import model_utils

# Extract classes for type annotations
Example = example_module.Example
Header = header_module.Header
Link = link_module.Link
MediaType = media_type_module.MediaType


class Response(BaseModel):
    """Represents an OpenAPI response object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    description: str | None = None
    content: dict[str, MediaType] = Field(default_factory=dict)
    headers: dict[str, Header] = Field(default_factory=dict)
    links: dict[str, Link] = Field(default_factory=dict)
    examples: dict[str, Example] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        """Create a Response from a dictionary."""
        excluded = {"description", "content", "headers", "links", "examples"}
        return cls(
            description=data.get("description"),
            content=model_utils.parse_collection(data, "content", media_type_module.MediaType.from_dict),
            headers=model_utils.parse_collection(data, "headers", header_module.Header.from_dict),
            links=model_utils.parse_collection(data, "links", link_module.Link.from_dict),
            examples=model_utils.parse_collection(data, "examples", example_module.Example.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
