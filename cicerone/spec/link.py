"""Link model for OpenAPI links.

References:
- OpenAPI 3.x Link Object: https://spec.openapis.org/oas/v3.1.0#link-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils
from cicerone.spec import server as spec_server


class Link(pydantic.BaseModel):
    """Represents an OpenAPI Link Object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow", "populate_by_name": True}

    # Keys renamed to snake_case fields in 0.4.0 that are still mirrored into
    # model_extra for backwards-compatible attribute access (removed in 0.5.0)
    MIRRORED_EXTRA_KEYS: typing.ClassVar[tuple[str, ...]] = ("operationRef", "operationId", "requestBody")

    operation_ref: str | None = pydantic.Field(None, alias="operationRef")
    operation_id: str | None = pydantic.Field(None, alias="operationId")
    parameters: dict[str, typing.Any] = pydantic.Field(default_factory=dict)
    request_body: typing.Any | None = pydantic.Field(None, alias="requestBody")
    description: str | None = None
    server: spec_server.Server | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "Link":
        """Create a Link from a dictionary."""
        link = cls(
            server=model_utils.parse_nested_object(data, "server", spec_server.Server.from_dict),
            **{k: v for k, v in data.items() if k != "server"},
        )
        model_utils.mirror_extras(link, data, cls.MIRRORED_EXTRA_KEYS)
        return link
