"""Components container model for reusable component definitions.

References:
- OpenAPI 3.x Components Object: https://spec.openapis.org/oas/v3.1.0#components-object
- Swagger 2.0 Definitions Object: https://swagger.io/specification/v2/#definitions-object
"""

from typing import Any, Mapping

from pydantic import BaseModel, Field

from cicerone.spec.example import Example
from cicerone.spec.header import Header
from cicerone.spec.parameter import Parameter
from cicerone.spec.request_body import RequestBody
from cicerone.spec.response import Response
from cicerone.spec.schema import Schema
from cicerone.spec.security_scheme import SecurityScheme
from cicerone.spec.version import Version


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
    links: dict[str, Any] = Field(default_factory=dict)
    callbacks: dict[str, Any] = Field(default_factory=dict)

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
    def from_spec(cls, raw: Mapping[str, Any], version: Version) -> "Components":
        """Create Components from spec data, handling both OpenAPI 3.x and Swagger 2.0."""
        schemas: dict[str, Schema] = {}
        responses: dict[str, Response] = {}
        parameters: dict[str, Parameter] = {}
        examples: dict[str, Example] = {}
        request_bodies: dict[str, RequestBody] = {}
        headers: dict[str, Header] = {}
        security_schemes: dict[str, SecurityScheme] = {}
        links: dict[str, Any] = {}
        callbacks: dict[str, Any] = {}

        # OpenAPI 3.x: components object
        if version.major >= 3 and "components" in raw:
            components = raw["components"]

            # Parse schemas
            if "schemas" in components:
                for name, schema_data in components["schemas"].items():
                    schemas[name] = Schema.from_dict(schema_data)

            # Parse typed component types
            if "responses" in components:
                for name, response_data in components["responses"].items():
                    responses[name] = Response.from_dict(response_data)

            if "parameters" in components:
                for name, param_data in components["parameters"].items():
                    parameters[name] = Parameter.from_dict(param_data)

            if "examples" in components:
                for name, example_data in components["examples"].items():
                    examples[name] = Example.from_dict(example_data)

            if "requestBodies" in components:
                for name, body_data in components["requestBodies"].items():
                    request_bodies[name] = RequestBody.from_dict(body_data)

            if "headers" in components:
                for name, header_data in components["headers"].items():
                    headers[name] = Header.from_dict(header_data)

            if "securitySchemes" in components:
                for name, scheme_data in components["securitySchemes"].items():
                    security_schemes[name] = SecurityScheme.from_dict(scheme_data)

            # Store remaining component types as raw data
            if "links" in components:
                links = dict(components["links"])

            if "callbacks" in components:
                callbacks = dict(components["callbacks"])

        # Swagger 2.0: definitions
        elif version.major == 2 and "definitions" in raw:
            for name, schema_data in raw["definitions"].items():
                schemas[name] = Schema.from_dict(schema_data)

            # Swagger 2.0 also has top-level parameters, responses, and securityDefinitions
            if "parameters" in raw:
                for name, param_data in raw["parameters"].items():
                    parameters[name] = Parameter.from_dict(param_data)

            if "responses" in raw:
                for name, response_data in raw["responses"].items():
                    responses[name] = Response.from_dict(response_data)

            if "securityDefinitions" in raw:
                for name, scheme_data in raw["securityDefinitions"].items():
                    security_schemes[name] = SecurityScheme.from_dict(scheme_data)

        return cls(
            schemas=schemas,
            responses=responses,
            parameters=parameters,
            examples=examples,
            requestBodies=request_bodies,
            headers=headers,
            securitySchemes=security_schemes,
            links=links,
            callbacks=callbacks,
        )
