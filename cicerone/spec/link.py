"""Link model for OpenAPI links.

References:
- OpenAPI 3.x Link Object: https://spec.openapis.org/oas/v3.1.0#link-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils
from cicerone.spec import server as spec_server


class Link(model_utils.SpecModel):
    """Represents an OpenAPI Link Object."""

    NESTED_FIELDS: typing.ClassVar[dict[str, model_utils.NestedField]] = {
        "server": model_utils.NestedField("object", spec_server.Server.from_dict),
    }

    # Keys renamed to snake_case fields in 0.4.0 that are still mirrored into
    # model_extra for backwards-compatible attribute access (removed in 0.5.0)
    MIRRORED_EXTRA_KEYS: typing.ClassVar[tuple[str, ...]] = ("operationRef", "operationId", "requestBody")

    operation_ref: str | None = pydantic.Field(None, alias="operationRef")
    operation_id: str | None = pydantic.Field(None, alias="operationId")
    parameters: dict[str, typing.Any] = pydantic.Field(default_factory=dict)
    request_body: typing.Any | None = pydantic.Field(None, alias="requestBody")
    description: str | None = None
    server: spec_server.Server | None = None
