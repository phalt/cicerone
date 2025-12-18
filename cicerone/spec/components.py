"""Components container model for reusable component definitions.

References:
- OpenAPI 3.x Components Object: https://spec.openapis.org/oas/v3.1.0#components-object
"""

from typing import Any, Mapping

from pydantic import BaseModel, Field

from cicerone.spec.callback import Callback
from cicerone.spec.example import Example
from cicerone.spec.header import Header
from cicerone.spec.link import Link
from cicerone.spec.model_utils import parse_collection
from cicerone.spec.parameter import Parameter
from cicerone.spec.request_body import RequestBody
from cicerone.spec.response import Response
from cicerone.spec.schema import Schema
from cicerone.spec.security_scheme import SecurityScheme


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
                schemas=parse_collection(components, "schemas", Schema.from_dict),
                responses=parse_collection(components, "responses", Response.from_dict),
                parameters=parse_collection(components, "parameters", Parameter.from_dict),
                examples=parse_collection(components, "examples", Example.from_dict),
                requestBodies=parse_collection(components, "requestBodies", RequestBody.from_dict),
                headers=parse_collection(components, "headers", Header.from_dict),
                securitySchemes=parse_collection(components, "securitySchemes", SecurityScheme.from_dict),
                links=parse_collection(components, "links", Link.from_dict),
                callbacks=parse_collection(components, "callbacks", Callback.from_dict),
            )

        return cls()
