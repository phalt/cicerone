"""Response model for OpenAPI responses.

References:
- OpenAPI 3.x Response Object: https://spec.openapis.org/oas/v3.1.0#response-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import example as spec_example
from cicerone.spec import header as spec_header
from cicerone.spec import link as spec_link
from cicerone.spec import media_type as spec_media_type
from cicerone.spec import model_utils


class Response(model_utils.SpecModel):
    """Represents an OpenAPI response object."""

    NESTED_FIELDS: typing.ClassVar[dict[str, model_utils.NestedField]] = {
        "content": model_utils.NestedField("collection", spec_media_type.MediaType.from_dict),
        "headers": model_utils.NestedField("collection", spec_header.Header.from_dict),
        "links": model_utils.NestedField("collection", spec_link.Link.from_dict),
        "examples": model_utils.NestedField("collection", spec_example.Example.from_dict),
    }

    # Keys promoted to typed fields in 0.4.0 that are still mirrored into
    # model_extra for backwards compatibility (removed in 0.5.0)
    MIRRORED_EXTRA_KEYS: typing.ClassVar[tuple[str, ...]] = ("$ref",)

    ref: str | None = pydantic.Field(None, alias="$ref")
    description: str | None = None
    content: dict[str, spec_media_type.MediaType] = pydantic.Field(default_factory=dict)
    headers: dict[str, spec_header.Header] = pydantic.Field(default_factory=dict)
    links: dict[str, spec_link.Link] = pydantic.Field(default_factory=dict)
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)
