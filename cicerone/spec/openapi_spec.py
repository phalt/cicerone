"""Top-level OpenAPISpec model."""

from typing import Any, Generator

from pydantic import BaseModel, model_validator

from cicerone.spec.components import Components
from cicerone.spec.operation import Operation
from cicerone.spec.paths import Paths
from cicerone.spec.version import Version


class OpenAPISpec(BaseModel):
    """Top-level OpenAPI specification model."""

    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    raw: dict[str, Any]
    version: Version
    paths: Paths
    components: Components

    @model_validator(mode="before")
    @classmethod
    def convert_version(cls, data: Any) -> Any:
        """Convert version string to Version object if needed."""
        if isinstance(data, dict) and "version" in data and isinstance(data["version"], str):
            data["version"] = Version(data["version"])
        return data

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
        """Yield all operations in the spec.

        Yields:
            Operation objects

        Example:
            >>> from cicerone.parse import parse_spec_from_file
            >>> spec = parse_spec_from_file("openapi.yaml")
            >>> for op in spec.all_operations():
            ...     print(op.method, op.path, op.operation_id)
        """
        yield from self.paths.all_operations()
