"""Operation model for HTTP operations.

References:
- OpenAPI 3.x Operation Object: https://spec.openapis.org/oas/v3.1.0#operation-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils
from cicerone.spec import parameter as spec_parameter
from cicerone.spec import request_body as spec_request_body
from cicerone.spec import response as spec_response
from cicerone.spec import server as spec_server
from cicerone.spec import tag as spec_tag


class Operation(pydantic.BaseModel):
    """Represents an HTTP operation (GET, POST, etc.)."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow", "populate_by_name": True}

    # Fields that are explicitly mapped in from_dict() to avoid double-processing
    EXPLICITLY_MAPPED_FIELDS: typing.ClassVar[set[str]] = {
        "operationId",
        "summary",
        "description",
        "tags",
        "parameters",
        "responses",
        "requestBody",
        "security",
        "callbacks",
        "deprecated",
        "servers",
        "externalDocs",
    }

    # Keys promoted to typed fields in 0.4.0 that are still mirrored into
    # model_extra for backwards compatibility (removed in 0.5.0)
    MIRRORED_EXTRA_KEYS: typing.ClassVar[tuple[str, ...]] = (
        "requestBody",
        "security",
        "callbacks",
        "deprecated",
        "servers",
        "externalDocs",
    )

    method: str
    path: str
    operation_id: str | None = pydantic.Field(None, alias="operationId")
    summary: str | None = None
    description: str | None = None
    tags: list[str] = pydantic.Field(default_factory=list)
    parameters: list[spec_parameter.Parameter] = pydantic.Field(default_factory=list)
    responses: dict[str, spec_response.Response] = pydantic.Field(default_factory=dict)
    request_body: spec_request_body.RequestBody | None = pydantic.Field(None, alias="requestBody")
    # None means "inherit the global security requirements", distinct from [] (no security)
    security: list[dict[str, list[str]]] | None = None
    callbacks: dict[str, "spec_callback.Callback"] = pydantic.Field(default_factory=dict)
    deprecated: bool = False
    servers: list[spec_server.Server] = pydantic.Field(default_factory=list)
    external_docs: spec_tag.ExternalDocumentation | None = pydantic.Field(None, alias="externalDocs")

    def __str__(self) -> str:
        """Return a readable string representation of the operation."""
        parts = [f"{self.method} {self.path}"]
        if self.operation_id:
            parts.append(f"id={self.operation_id}")
        if self.summary:
            parts.append(f"'{self.summary}'")
        if self.tags:
            parts.append(f"tags={self.tags}")
        if self.deprecated:
            parts.append("deprecated")
        return f"<Operation: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, method: str, path: str, data: typing.Mapping[str, typing.Any]) -> "Operation":
        """Create an Operation from a dictionary."""
        # Skip non-dict entries so malformed specs degrade gracefully; the raw
        # values are still available via the mirrored model_extra copies
        parameters_data = data.get("parameters", [])
        responses_data = data.get("responses", {})
        request_body_data = data.get("requestBody")
        security_data = data.get("security")
        callbacks_data = data.get("callbacks", {})
        external_docs_data = data.get("externalDocs")
        operation = cls(
            method=method,
            path=path,
            operationId=data.get("operationId"),
            summary=data.get("summary"),
            description=data.get("description"),
            tags=data.get("tags", []),
            parameters=[
                spec_parameter.Parameter.from_dict(p)
                for p in (parameters_data if isinstance(parameters_data, list) else [])
                if isinstance(p, dict)
            ],
            responses={
                status: spec_response.Response.from_dict(response_data)
                for status, response_data in (
                    responses_data.items() if isinstance(responses_data, typing.Mapping) else []
                )
                if isinstance(response_data, dict)
            },
            requestBody=(
                spec_request_body.RequestBody.from_dict(request_body_data)
                if isinstance(request_body_data, dict)
                else None
            ),
            security=security_data if isinstance(security_data, list) else None,
            callbacks={
                expression: spec_callback.Callback.from_dict(callback_data)
                for expression, callback_data in (
                    callbacks_data.items() if isinstance(callbacks_data, typing.Mapping) else []
                )
                if isinstance(callback_data, dict)
            },
            deprecated=data.get("deprecated", False),
            servers=[
                spec_server.Server.from_dict(s) for s in data.get("servers", []) if isinstance(s, dict) and "url" in s
            ],
            externalDocs=(
                spec_tag.ExternalDocumentation.from_dict(external_docs_data)
                if isinstance(external_docs_data, dict) and "url" in external_docs_data
                else None
            ),
            **{k: v for k, v in data.items() if k not in cls.EXPLICITLY_MAPPED_FIELDS},
        )
        model_utils.mirror_extras(operation, data, cls.MIRRORED_EXTRA_KEYS)
        return operation


# Imported after the class definition to break the import cycle:
# operation -> callback -> path_item -> operation
from cicerone.spec import callback as spec_callback  # noqa: E402

# When callback.py is mid-import (it imports operation via path_item), the rebuild
# cannot complete yet; cicerone/spec/__init__.py performs the final rebuild
if hasattr(spec_callback, "Callback"):
    Operation.model_rebuild(raise_errors=False)
