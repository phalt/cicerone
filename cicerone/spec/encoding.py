"""Encoding model for OpenAPI encoding objects.

References:
- OpenAPI 3.x Encoding Object: https://spec.openapis.org/oas/v3.1.0#encoding-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import header as spec_header
from cicerone.spec import model_utils


class Encoding(model_utils.SpecModel):
    """Represents an OpenAPI Encoding Object.

    An encoding definition applied to a single schema property.
    """

    NESTED_FIELDS: typing.ClassVar[dict[str, model_utils.NestedField]] = {
        "headers": model_utils.NestedField("collection", spec_header.Header.from_dict),
    }

    contentType: str | None = None
    headers: dict[str, spec_header.Header] = pydantic.Field(default_factory=dict)
    style: str | None = None
    explode: bool = False
    allowReserved: bool = False
