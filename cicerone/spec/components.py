"""Components container model for reusable component definitions.

References:
- OpenAPI 3.x Components Object: https://spec.openapis.org/oas/v3.1.0#components-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import callback as spec_callback
from cicerone.spec import example as spec_example
from cicerone.spec import header as spec_header
from cicerone.spec import link as spec_link
from cicerone.spec import model_utils
from cicerone.spec import parameter as spec_parameter
from cicerone.spec import request_body as spec_request_body
from cicerone.spec import response as spec_response
from cicerone.spec import schema as spec_schema
from cicerone.spec import security_scheme as spec_security_scheme


class Components(pydantic.BaseModel):
    """Container for reusable component definitions."""

    # Allow extra fields to support:
    # - Vendor extensions (x-* fields) per OpenAPI spec
    # - Future spec additions without breaking compatibility
    # - Preservation of all data for raw access
    # populate_by_name: Allow using either field name or alias
    model_config = {"extra": "allow", "populate_by_name": True}

    schemas: dict[str, spec_schema.Schema] = pydantic.Field(default_factory=dict)
    responses: dict[str, spec_response.Response] = pydantic.Field(default_factory=dict)
    parameters: dict[str, spec_parameter.Parameter] = pydantic.Field(default_factory=dict)
    examples: dict[str, spec_example.Example] = pydantic.Field(default_factory=dict)
    request_bodies: dict[str, spec_request_body.RequestBody] = pydantic.Field(
        default_factory=dict, alias="requestBodies"
    )
    headers: dict[str, spec_header.Header] = pydantic.Field(default_factory=dict)
    security_schemes: dict[str, spec_security_scheme.SecurityScheme] = pydantic.Field(
        default_factory=dict, alias="securitySchemes"
    )
    links: dict[str, spec_link.Link] = pydantic.Field(default_factory=dict)
    callbacks: dict[str, spec_callback.Callback] = pydantic.Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of the components container."""
        component_info = [
            ("schemas", self.schemas),
            ("responses", self.responses),
            ("parameters", self.parameters),
            ("requestBodies", self.request_bodies),
            ("examples", self.examples),
            ("securitySchemes", self.security_schemes),
            ("headers", self.headers),
            ("links", self.links),
            ("callbacks", self.callbacks),
        ]

        parts = [f"{len(items)} {name}" for name, items in component_info if items]

        if not parts:
            return "<Components: empty>"

        # Show first few component types and count
        summary = ", ".join(parts[:3])
        if len(parts) > 3:
            summary += f" (+{len(parts) - 3} more types)"

        return f"<Components: {summary}>"

    def get_schema(self, schema_name: str) -> spec_schema.Schema | None:
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
                schemas=model_utils.parse_collection(components, "schemas", spec_schema.Schema.from_dict),
                responses=model_utils.parse_collection(components, "responses", spec_response.Response.from_dict),
                parameters=model_utils.parse_collection(components, "parameters", spec_parameter.Parameter.from_dict),
                examples=model_utils.parse_collection(components, "examples", spec_example.Example.from_dict),
                request_bodies=model_utils.parse_collection(
                    components, "requestBodies", spec_request_body.RequestBody.from_dict
                ),
                headers=model_utils.parse_collection(components, "headers", spec_header.Header.from_dict),
                security_schemes=model_utils.parse_collection(
                    components, "securitySchemes", spec_security_scheme.SecurityScheme.from_dict
                ),
                links=model_utils.parse_collection(components, "links", spec_link.Link.from_dict),
                callbacks=model_utils.parse_collection(components, "callbacks", spec_callback.Callback.from_dict),
            )

        return cls()
