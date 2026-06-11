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


class MediaType(model_utils.SpecModel):
    """Represents an OpenAPI Media Type Object."""

    NESTED_FIELDS: typing.ClassVar[dict[str, model_utils.NestedField]] = {
        "schema": model_utils.NestedField("object", spec_schema.Schema.from_dict),
        "examples": model_utils.NestedField("collection", spec_example.Example.from_dict),
        "encoding": model_utils.NestedField("collection", spec_encoding.Encoding.from_dict),
    }

    schema_: spec_schema.Schema | None = pydantic.Field(None, alias="schema")
    example: typing.Any | None = None
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)
    encoding: dict[str, spec_encoding.Encoding] = pydantic.Field(default_factory=dict)
