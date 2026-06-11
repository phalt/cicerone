"""Example model for OpenAPI examples.

References:
- OpenAPI 3.x Example Object: https://spec.openapis.org/oas/v3.1.0#example-object
"""

import typing

from cicerone.spec import model_utils


class Example(model_utils.SpecModel):
    """Represents an OpenAPI example object."""

    summary: str | None = None
    description: str | None = None
    value: typing.Any | None = None
    externalValue: str | None = None

    # Malformed scalar values fall back to the field default instead of
    # rejecting the whole document
    _lenient_scalars = model_utils.lenient_validator("summary", "description", "externalValue")
