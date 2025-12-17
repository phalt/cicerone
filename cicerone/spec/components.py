"""Components container model for reusable component definitions.

References:
- OpenAPI 3.x Components Object: https://spec.openapis.org/oas/v3.1.0#components-object
- Swagger 2.0 Definitions Object: https://swagger.io/specification/v2/#definitions-object
"""

from typing import Any, Mapping

from pydantic import BaseModel, Field

from cicerone.spec.schema import Schema
from cicerone.spec.version import Version


class Components(BaseModel):
    """Container for reusable component definitions."""

    # Allow extra fields to support:
    # - Vendor extensions (x-* fields) per OpenAPI spec
    # - Future spec additions without breaking compatibility
    # - Preservation of all data for raw access
    model_config = {"extra": "allow"}

    schemas: dict[str, Schema] = Field(default_factory=dict)
    responses: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    examples: dict[str, Any] = Field(default_factory=dict)
    requestBodies: dict[str, Any] = Field(default_factory=dict, alias="requestBodies")
    headers: dict[str, Any] = Field(default_factory=dict)
    securitySchemes: dict[str, Any] = Field(default_factory=dict, alias="securitySchemes")
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
        if self.requestBodies:
            parts.append(f"{len(self.requestBodies)} requestBodies")
        if self.examples:
            parts.append(f"{len(self.examples)} examples")
        if self.securitySchemes:
            parts.append(f"{len(self.securitySchemes)} securitySchemes")
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
        schemas = {}
        responses = {}
        parameters = {}
        examples = {}
        request_bodies = {}
        headers = {}
        security_schemes = {}
        links = {}
        callbacks = {}

        # OpenAPI 3.x: components object
        if version.major >= 3 and "components" in raw:
            components = raw["components"]

            # Parse schemas
            if "schemas" in components:
                for name, schema_data in components["schemas"].items():
                    schemas[name] = Schema.from_dict(schema_data)

            # Store other component types as raw data for now
            if "responses" in components:
                responses = dict(components["responses"])
            if "parameters" in components:
                parameters = dict(components["parameters"])
            if "examples" in components:
                examples = dict(components["examples"])
            if "requestBodies" in components:
                request_bodies = dict(components["requestBodies"])
            if "headers" in components:
                headers = dict(components["headers"])
            if "securitySchemes" in components:
                security_schemes = dict(components["securitySchemes"])
            if "links" in components:
                links = dict(components["links"])
            if "callbacks" in components:
                callbacks = dict(components["callbacks"])

        # Swagger 2.0: definitions
        elif version.major == 2 and "definitions" in raw:
            for name, schema_data in raw["definitions"].items():
                schemas[name] = Schema.from_dict(schema_data)

            # Swagger 2.0 also has top-level parameters and responses
            if "parameters" in raw:
                parameters = dict(raw["parameters"])
            if "responses" in raw:
                responses = dict(raw["responses"])
            if "securityDefinitions" in raw:
                security_schemes = dict(raw["securityDefinitions"])

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
