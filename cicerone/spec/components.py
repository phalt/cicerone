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
    # populate_by_name: Allow using either field name or alias
    model_config = {"extra": "allow", "populate_by_name": True}

    schemas: dict[str, Schema] = Field(default_factory=dict)
    responses: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    examples: dict[str, Any] = Field(default_factory=dict)
    request_bodies: dict[str, Any] = Field(default_factory=dict, alias="requestBodies")
    headers: dict[str, Any] = Field(default_factory=dict)
    security_schemes: dict[str, Any] = Field(default_factory=dict, alias="securitySchemes")
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
        responses: dict[str, Any] = {}
        parameters: dict[str, Any] = {}
        examples: dict[str, Any] = {}
        request_bodies: dict[str, Any] = {}
        headers: dict[str, Any] = {}
        security_schemes: dict[str, Any] = {}
        links: dict[str, Any] = {}
        callbacks: dict[str, Any] = {}

        # OpenAPI 3.x: components object
        if version.major >= 3 and "components" in raw:
            components = raw["components"]

            # Parse schemas
            if "schemas" in components:
                for name, schema_data in components["schemas"].items():
                    schemas[name] = Schema.from_dict(schema_data)

            # Store other component types as raw data for now
            component_mappings = {
                "responses": responses,
                "parameters": parameters,
                "examples": examples,
                "requestBodies": request_bodies,
                "headers": headers,
                "securitySchemes": security_schemes,
                "links": links,
                "callbacks": callbacks,
            }

            for component_key, target_dict in component_mappings.items():
                if component_key in components:
                    target_dict.update(components[component_key])

        # Swagger 2.0: definitions
        elif version.major == 2 and "definitions" in raw:
            for name, schema_data in raw["definitions"].items():
                schemas[name] = Schema.from_dict(schema_data)

            # Swagger 2.0 also has top-level parameters and responses
            swagger_mappings = {
                "parameters": parameters,
                "responses": responses,
                "securityDefinitions": security_schemes,
            }

            for swagger_key, target_dict in swagger_mappings.items():
                if swagger_key in raw:
                    target_dict.update(raw[swagger_key])

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
