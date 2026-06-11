"""PathItem model representing a single path with operations.

References:
- OpenAPI 3.x Path Item Object: https://spec.openapis.org/oas/v3.1.0#path-item-object
"""

import typing

import pydantic

from cicerone.spec import operation as spec_operation
from cicerone.spec import parameter as spec_parameter

HTTP_METHODS = ["get", "post", "put", "patch", "delete", "options", "head", "trace"]


class PathItem(pydantic.BaseModel):
    """Represents a path item with its operations."""

    # Allow extra fields to support vendor extensions and path-level parameters
    model_config = {"extra": "allow", "populate_by_name": True}

    path: str
    ref: str | None = pydantic.Field(None, alias="$ref")
    summary: str | None = None
    description: str | None = None
    operations: dict[str, spec_operation.Operation] = pydantic.Field(default_factory=dict)
    # Path-level parameters, also merged into each operation's parameters below
    parameters: list[spec_parameter.Parameter] = pydantic.Field(default_factory=list)

    def __str__(self) -> str:
        """Return a readable string representation of the path item."""
        methods = ", ".join(m.upper() for m in self.operations.keys())
        return f"<PathItem: {self.path} [{methods}]>"

    @classmethod
    def from_dict(cls, path: str, data: typing.Mapping[str, typing.Any]) -> "PathItem":
        """Create a PathItem from a dictionary."""
        operations = {}

        # Note: We check isinstance as a defensive measure because some callers
        # (like callbacks with invalid test data) may pass non-Mapping types
        if not isinstance(data, typing.Mapping):
            return cls(path=path)

        # Extract path-level parameters if they exist
        path_level_parameters = data.get("parameters", [])
        if not isinstance(path_level_parameters, list):
            path_level_parameters = []

        for method in HTTP_METHODS:
            if method in data:
                # Only create a copy if we need to merge path-level parameters
                if path_level_parameters:
                    operation_data = dict(data[method])
                    # Merge path-level parameters with operation-level parameters
                    # Path-level parameters come first, operation-level parameters come after
                    operation_params = operation_data.get("parameters", [])
                    operation_data["parameters"] = path_level_parameters + operation_params
                    operations[method] = spec_operation.Operation.from_dict(method.upper(), path, operation_data)
                else:
                    # No path-level parameters, use operation data as-is
                    operations[method] = spec_operation.Operation.from_dict(method.upper(), path, data[method])

        excluded = set(HTTP_METHODS) | {"parameters", "summary", "description", "$ref"}
        return cls(
            path=path,
            operations=operations,
            summary=data.get("summary"),
            description=data.get("description"),
            parameters=[spec_parameter.Parameter.from_dict(p) for p in path_level_parameters if isinstance(p, dict)],
            **{"$ref": data.get("$ref")} if "$ref" in data else {},
            **{k: v for k, v in data.items() if k not in excluded},
        )
