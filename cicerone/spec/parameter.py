"""Parameter model for OpenAPI parameters.

References:
- OpenAPI 3.x Parameter Object: https://spec.openapis.org/oas/v3.1.0#parameter-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import example as spec_example
from cicerone.spec import model_utils
from cicerone.spec import schema as spec_schema


class Parameter(model_utils.SpecModel):
    """Represents an OpenAPI parameter object."""

    NESTED_FIELDS: typing.ClassVar[dict[str, model_utils.NestedField]] = {
        "schema": model_utils.NestedField("object", spec_schema.Schema.from_dict),
        "examples": model_utils.NestedField("collection", spec_example.Example.from_dict),
    }

    # Keys promoted to typed fields in 0.4.0 that are still mirrored into
    # model_extra for backwards compatibility (removed in 0.5.0)
    MIRRORED_EXTRA_KEYS: typing.ClassVar[tuple[str, ...]] = ("$ref", "deprecated", "allowEmptyValue")

    ref: str | None = pydantic.Field(None, alias="$ref")
    name: str | None = None
    in_: str | None = pydantic.Field(None, alias="in")
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    allow_empty_value: bool | None = pydantic.Field(None, alias="allowEmptyValue")
    schema_: spec_schema.Schema | None = pydantic.Field(None, alias="schema")
    # OpenAPI 3.x fields
    style: str | None = None
    explode: bool | None = None
    example: typing.Any | None = None
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)

    # Malformed scalar values fall back to the field default instead of
    # rejecting the whole document
    _lenient_scalars = model_utils.lenient_validator(
        "ref", "name", "in_", "description", "required", "deprecated", "allow_empty_value", "style", "explode"
    )
