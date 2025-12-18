"""MediaType model for OpenAPI media type objects.

References:
- OpenAPI 3.x Media Type Object: https://spec.openapis.org/oas/v3.1.0#media-type-object
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from cicerone.spec.encoding import Encoding
from cicerone.spec.example import Example
from cicerone.spec.model_utils import parse_collection


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
            examples=parse_collection(data, "examples", Example.from_dict),
            encoding=parse_collection(data, "encoding", Encoding.from_dict),
            **{k: v for k, v in data.items() if k not in {"schema", "example", "examples", "encoding"}},
        )
