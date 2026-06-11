"""RequestBody model for OpenAPI request bodies.

References:
- OpenAPI 3.x Request Body Object: https://spec.openapis.org/oas/v3.1.0#request-body-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import media_type as spec_media_type
from cicerone.spec import model_utils


class RequestBody(model_utils.SpecModel):
    """Represents an OpenAPI request body object."""

    NESTED_FIELDS: typing.ClassVar[dict[str, model_utils.NestedField]] = {
        "content": model_utils.NestedField("collection", spec_media_type.MediaType.from_dict),
    }

    # Keys promoted to typed fields in 0.4.0 that are still mirrored into
    # model_extra for backwards compatibility (removed in 0.5.0)
    MIRRORED_EXTRA_KEYS: typing.ClassVar[tuple[str, ...]] = ("$ref",)

    ref: str | None = pydantic.Field(None, alias="$ref")
    description: str | None = None
    content: dict[str, spec_media_type.MediaType] = pydantic.Field(default_factory=dict)
    required: bool = False

    # Malformed scalar values fall back to the field default instead of
    # rejecting the whole document
    _lenient_scalars = model_utils.lenient_validator("ref", "description", "required")
