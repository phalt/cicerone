"""MediaType model for OpenAPI media type objects.

References:
- OpenAPI 3.x Media Type Object: https://spec.openapis.org/oas/v3.1.0#media-type-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec import encoding as encoding_module
from cicerone.spec import example as example_module
from cicerone.spec import model_utils

# Extract classes for type annotations
Encoding = encoding_module.Encoding
Example = example_module.Example


class MediaType(BaseModel):
    """Represents an OpenAPI Media Type Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    schema_: dict[str, Any] | None = Field(None, alias="schema")
    example: Any | None = None
    examples: dict[str, Example] = Field(default_factory=dict)
    encoding: dict[str, Encoding] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MediaType:
        """Create a MediaType from a dictionary."""
        return cls(
            schema=data.get("schema"),
            example=data.get("example"),
            examples=model_utils.parse_collection(data, "examples", example_module.Example.from_dict),
            encoding=model_utils.parse_collection(data, "encoding", encoding_module.Encoding.from_dict),
            **{k: v for k, v in data.items() if k not in {"schema", "example", "examples", "encoding"}},
        )
