"""MediaType model for OpenAPI media type objects.

References:
- OpenAPI 3.x Media Type Object: https://spec.openapis.org/oas/v3.1.0#media-type-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import encoding as spec_encoding
from cicerone.spec import example as spec_example
from cicerone.spec import model_utils
from cicerone.spec import schema as spec_schema


class MediaType(pydantic.BaseModel):
    """Represents an OpenAPI Media Type Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow", "populate_by_name": True}

    schema_: spec_schema.Schema | None = pydantic.Field(None, alias="schema")
    example: typing.Any | None = None
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)
    encoding: dict[str, spec_encoding.Encoding] = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> MediaType:
        """Create a MediaType from a dictionary."""
        # JSON Schema allows boolean schemas (true/false); only parse dict values
        schema_value = data.get("schema")
        return cls(
            schema=spec_schema.Schema.from_dict(schema_value) if isinstance(schema_value, dict) else None,
            example=data.get("example"),
            examples=model_utils.parse_collection(data, "examples", spec_example.Example.from_dict),
            encoding=model_utils.parse_collection(data, "encoding", spec_encoding.Encoding.from_dict),
            **{k: v for k, v in data.items() if k not in {"schema", "example", "examples", "encoding"}},
        )
