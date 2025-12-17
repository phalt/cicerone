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

    def __str__(self) -> str:
        """Return a readable string representation of the components container."""
        num_schemas = len(self.schemas)
        schemas_preview = ", ".join(list(self.schemas.keys())[:5])
        if num_schemas > 5:
            schemas_preview += f", ... (+{num_schemas - 5} more)"
        return f"<Components: {num_schemas} schemas [{schemas_preview}]>"

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

        # OpenAPI 3.x: components.schemas
        if version.major >= 3 and "components" in raw and "schemas" in raw["components"]:
            for name, schema_data in raw["components"]["schemas"].items():
                schemas[name] = Schema.from_dict(schema_data)

        # Swagger 2.0: definitions
        elif version.major == 2 and "definitions" in raw:
            for name, schema_data in raw["definitions"].items():
                schemas[name] = Schema.from_dict(schema_data)

        return cls(schemas=schemas)
