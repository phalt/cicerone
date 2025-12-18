"""Components container model for reusable component definitions.

References:
- OpenAPI 3.x Components Object: https://spec.openapis.org/oas/v3.1.0#components-object
"""

from typing import Any, Mapping

from pydantic import BaseModel, Field

from cicerone.spec import callback as callback_module
from cicerone.spec import example as example_module
from cicerone.spec import header as header_module
from cicerone.spec import link as link_module
from cicerone.spec import model_utils
from cicerone.spec import parameter as parameter_module
from cicerone.spec import request_body as request_body_module
from cicerone.spec import response as response_module
from cicerone.spec import schema as schema_module
from cicerone.spec import security_scheme as security_scheme_module

# Extract classes for type annotations
Callback = callback_module.Callback
Example = example_module.Example
Header = header_module.Header
Link = link_module.Link
Parameter = parameter_module.Parameter
RequestBody = request_body_module.RequestBody
Response = response_module.Response
Schema = schema_module.Schema
SecurityScheme = security_scheme_module.SecurityScheme


class Components(BaseModel):
    """Container for reusable component definitions."""

    # Allow extra fields to support:
    # - Vendor extensions (x-* fields) per OpenAPI spec
    # - Future spec additions without breaking compatibility
    # - Preservation of all data for raw access
    # populate_by_name: Allow using either field name or alias
    model_config = {"extra": "allow", "populate_by_name": True}

    schemas: dict[str, Schema] = Field(default_factory=dict)
    responses: dict[str, Response] = Field(default_factory=dict)
    parameters: dict[str, Parameter] = Field(default_factory=dict)
    examples: dict[str, Example] = Field(default_factory=dict)
    request_bodies: dict[str, RequestBody] = Field(default_factory=dict, alias="requestBodies")
    headers: dict[str, Header] = Field(default_factory=dict)
    security_schemes: dict[str, SecurityScheme] = Field(default_factory=dict, alias="securitySchemes")
    links: dict[str, Link] = Field(default_factory=dict)
    callbacks: dict[str, Callback] = Field(default_factory=dict)

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

    def get_schema(self, schema_name: str) -> Schema | None:
        """Get a schema by name.

        Args:
            schema_name: Name of the schema to retrieve

        Returns:
            Schema object if found, None otherwise
        """
        return self.schemas.get(schema_name)

    @classmethod
    def from_spec(cls, raw: Mapping[str, Any]) -> "Components":
        """Create Components from spec data."""
        # OpenAPI 3.x: components object
        if "components" in raw:
            components = raw["components"]
            return cls(
                schemas=model_utils.parse_collection(components, "schemas", schema_module.Schema.from_dict),
                responses=model_utils.parse_collection(components, "responses", response_module.Response.from_dict),
                parameters=model_utils.parse_collection(components, "parameters", parameter_module.Parameter.from_dict),
                examples=model_utils.parse_collection(components, "examples", example_module.Example.from_dict),
                requestBodies=model_utils.parse_collection(
                    components, "requestBodies", request_body_module.RequestBody.from_dict
                ),
                headers=model_utils.parse_collection(components, "headers", header_module.Header.from_dict),
                securitySchemes=model_utils.parse_collection(
                    components, "securitySchemes", security_scheme_module.SecurityScheme.from_dict
                ),
                links=model_utils.parse_collection(components, "links", link_module.Link.from_dict),
                callbacks=model_utils.parse_collection(components, "callbacks", callback_module.Callback.from_dict),
            )

        return cls()
