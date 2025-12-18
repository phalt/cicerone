"""Top-level OpenAPISpec model.

References:
- OpenAPI 3.x Specification: https://spec.openapis.org/oas/v3.1.0
"""

from __future__ import annotations

from itertools import chain
from typing import Any, Generator

from pydantic import BaseModel, Field

from cicerone.spec import components as components_module
from cicerone.spec import info as info_module
from cicerone.spec import operation as operation_module
from cicerone.spec import paths as paths_module
from cicerone.spec import server as server_module
from cicerone.spec import tag as tag_module
from cicerone.spec import version as version_module
from cicerone.spec import webhooks as webhooks_module

# Extract classes for type annotations
Components = components_module.Components
Info = info_module.Info
Operation = operation_module.Operation
Paths = paths_module.Paths
Server = server_module.Server
Tag = tag_module.Tag
ExternalDocumentation = tag_module.ExternalDocumentation
Version = version_module.Version
Webhooks = webhooks_module.Webhooks


class OpenAPISpec(BaseModel):
    """Top-level OpenAPI specification model."""

    # Model configuration:
    # - extra="allow": Supports vendor extensions (x-* fields) and preserves all spec data
    # - arbitrary_types_allowed=True: Required for the custom Version class (non-Pydantic)
    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    raw: dict[str, Any]
    version: Version
    info: Info | None = None
    json_schema_dialect: str | None = Field(None, alias="jsonSchemaDialect")
    servers: list[Server] = Field(default_factory=list)
    paths: Paths
    webhooks: Webhooks = Field(default_factory=lambda: webhooks_module.Webhooks(items={}))
    components: Components
    security: list[dict[str, list[str]]] = Field(default_factory=list)
    tags: list[Tag] = Field(default_factory=list)
    external_docs: ExternalDocumentation | None = Field(None, alias="externalDocs")

    def __str__(self) -> str:
        """Return a readable string representation of the OpenAPI spec."""
        title = self.raw.get("info", {}).get("title", "Untitled")
        num_paths = len(self.paths.items)
        num_schemas = len(self.components.schemas)
        return f"<OpenAPISpec: '{title}' v{self.version}, {num_paths} paths, {num_schemas} schemas>"

    def operation_by_operation_id(self, operation_id: str) -> Operation | None:
        """Find an operation by its operationId.

        Args:
            operation_id: The operationId to search for

        Returns:
            The Operation if found, None otherwise

        Example:
            >>> from cicerone.parse import parse_spec_from_file
            >>> spec = parse_spec_from_file("openapi.yaml")
            >>> op = spec.operation_by_operation_id("listUsers")
        """
        for operation_obj in self.paths.all_operations():
            if operation_obj.operation_id == operation_id:
                return operation_obj
        return None

    def all_operations(self) -> Generator[Operation, None, None]:
        """Yield all operations in the spec (from paths and webhooks).

        Yields:
            Operation objects

        Example:
            >>> from cicerone.parse import parse_spec_from_file
            >>> spec = parse_spec_from_file("openapi.yaml")
            >>> for op in spec.all_operations():
            ...     print(op.method, op.path, op.operation_id)
        """
        yield from chain(self.paths.all_operations(), self.webhooks.all_operations())
