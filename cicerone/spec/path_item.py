"""PathItem model representing a single path with operations."""

from typing import Any, Mapping

from pydantic import BaseModel, Field

from cicerone.spec.operation import Operation


class PathItem(BaseModel):
    """Represents a path item with its operations."""

    model_config = {"extra": "allow"}

    path: str
    operations: dict[str, Operation] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, path: str, data: Mapping[str, Any]) -> "PathItem":
        """Create a PathItem from a dictionary."""
        operations = {}
        http_methods = ["get", "post", "put", "patch", "delete", "options", "head", "trace"]

        for method in http_methods:
            if method in data:
                operations[method] = Operation.from_dict(method.upper(), path, data[method])

        return cls(path=path, operations=operations)
