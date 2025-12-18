"""Top-level OpenAPISpec model.

References:
- OpenAPI 3.x Specification: https://spec.openapis.org/oas/v3.1.0
"""

from typing import Any, Generator

from pydantic import BaseModel, Field

from cicerone.spec.components import Components
from cicerone.spec.info import Info
from cicerone.spec.operation import Operation
from cicerone.spec.paths import Paths
from cicerone.spec.server import Server
from cicerone.spec.tag import Tag
from cicerone.spec.version import Version
from cicerone.spec.webhooks import Webhooks


class OpenAPISpec(BaseModel):
    """Top-level OpenAPI specification model."""

    # Model configuration:
    # - extra="allow": Supports vendor extensions (x-* fields) and preserves all spec data
    # - arbitrary_types_allowed=True: Required for the custom Version class (non-Pydantic)
    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    raw: dict[str, Any]
    version: Version
    info: Info | None = None
    paths: Paths
    webhooks: Webhooks = Field(default_factory=lambda: Webhooks(items={}))
    components: Components
    servers: list[Server] = Field(default_factory=list)
    tags: list[Tag] = Field(default_factory=list)

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
        for operation in self.paths.all_operations():
            if operation.operation_id == operation_id:
                return operation
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
        yield from self.paths.all_operations()
        yield from self.webhooks.all_operations()
