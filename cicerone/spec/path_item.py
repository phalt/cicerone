"""PathItem model representing a single path with operations.

References:
- OpenAPI 3.x Path Item Object: https://spec.openapis.org/oas/v3.1.0#path-item-object
"""

import typing

import pydantic

from cicerone.spec import operation as spec_operation


class PathItem(pydantic.BaseModel):
    """Represents a path item with its operations."""

    # Allow extra fields to support vendor extensions and path-level parameters
    model_config = {"extra": "allow"}

    path: str
    operations: dict[str, spec_operation.Operation] = pydantic.Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of the path item."""
        methods = ", ".join(m.upper() for m in self.operations.keys())
        return f"<PathItem: {self.path} [{methods}]>"

    @classmethod
    def from_dict(cls, path: str, data: typing.Mapping[str, typing.Any]) -> "PathItem":
        """Create a PathItem from a dictionary."""
        operations = {}
        http_methods = ["get", "post", "put", "patch", "delete", "options", "head", "trace"]

        for method in http_methods:
            if method in data:
                operations[method] = spec_operation.Operation.from_dict(method.upper(), path, data[method])

        return cls(path=path, operations=operations)
