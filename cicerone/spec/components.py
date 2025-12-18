"""Components container model for reusable component definitions.

References:
- OpenAPI 3.x Components Object: https://spec.openapis.org/oas/v3.1.0#components-object
"""

from __future__ import annotations


import typing

import pydantic

from cicerone.spec import (
    callback,
    example,
    header,
    link,
    model_utils,
    parameter,
    request_body,
    response,
    schema,
    security_scheme,
)


class Components(pydantic.BaseModel):
    """Container for reusable component definitions."""

    # Allow extra fields to support:
    # - Vendor extensions (x-* fields) per OpenAPI spec
    # - Future spec additions without breaking compatibility
    # - Preservation of all data for raw access
    # populate_by_name: Allow using either field name or alias
    model_config = {"extra": "allow", "populate_by_name": True}

    schemas: "dict[str, schema.Schema]" = pydantic.Field(default_factory=dict)
    responses: "dict[str, response.Response]" = pydantic.Field(default_factory=dict)
    parameters: "dict[str, parameter.Parameter]" = pydantic.Field(default_factory=dict)
    examples: "dict[str, example.Example]" = pydantic.Field(default_factory=dict)
    request_bodies: "dict[str, request_body.RequestBody]" = pydantic.Field(default_factory=dict, alias="requestBodies")
    headers: "dict[str, header.Header]" = pydantic.Field(default_factory=dict)
    security_schemes: "dict[str, security_scheme.SecurityScheme]" = pydantic.Field(
        default_factory=dict, alias="securitySchemes"
    )
    links: "dict[str, link.Link]" = pydantic.Field(default_factory=dict)
    callbacks: "dict[str, callback.Callback]" = pydantic.Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of the components container."""
        parts = []
        if self.schemas:
            parts.append(f"{len(self.schemas)} schemas")
        if self.responses:
            parts.append(f"{len(self.responses)} responses")
        if self.parameters:
            parts.append(f"{len(self.parameters)} parameters")
        if self.request_bodies:
            parts.append(f"{len(self.request_bodies)} requestBodies")
        if self.examples:
            parts.append(f"{len(self.examples)} examples")
        if self.security_schemes:
            parts.append(f"{len(self.security_schemes)} securitySchemes")
        if self.headers:
            parts.append(f"{len(self.headers)} headers")
        if self.links:
            parts.append(f"{len(self.links)} links")
        if self.callbacks:
            parts.append(f"{len(self.callbacks)} callbacks")

        if not parts:
            return "<Components: empty>"

        # Show first few component types and count
        summary = ", ".join(parts[:3])
        if len(parts) > 3:
            summary += f" (+{len(parts) - 3} more types)"

        return f"<Components: {summary}>"

    def get_schema(self, schema_name: str) -> schema.Schema | None:
        """Get a schema by name.

        Args:
            schema_name: Name of the schema to retrieve

        Returns:
            Schema object if found, None otherwise
        """
        return self.schemas.get(schema_name)

    @classmethod
    def from_spec(cls, raw: typing.Mapping[str, typing.Any]) -> "Components":
        """Create Components from spec data."""
        # OpenAPI 3.x: components object
        if "components" in raw:
            components = raw["components"]
            return cls(
                schemas=model_utils.parse_collection(components, "schemas", schema.Schema.from_dict),
                responses=model_utils.parse_collection(components, "responses", response.Response.from_dict),
                parameters=model_utils.parse_collection(components, "parameters", parameter.Parameter.from_dict),
                examples=model_utils.parse_collection(components, "examples", example.Example.from_dict),
                requestBodies=model_utils.parse_collection(
                    components, "requestBodies", request_body.RequestBody.from_dict
                ),
                headers=model_utils.parse_collection(components, "headers", header.Header.from_dict),
                securitySchemes=model_utils.parse_collection(
                    components, "securitySchemes", security_scheme.SecurityScheme.from_dict
                ),
                links=model_utils.parse_collection(components, "links", link.Link.from_dict),
                callbacks=model_utils.parse_collection(components, "callbacks", callback.Callback.from_dict),
            )

        return cls()
