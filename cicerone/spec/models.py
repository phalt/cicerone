"""Core pydantic models for OpenAPI specification parsing and traversal."""

import json
from pathlib import Path
from typing import Any, Generator, Mapping
from urllib.request import Request, urlopen

import yaml
from pydantic import BaseModel, Field, model_validator


class Version:
    """Simple version representation for OpenAPI/Swagger specs."""

    def __init__(self, version_string: str):
        self.raw = version_string
        parts = version_string.split(".")
        self.major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
        self.minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        self.patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

    def __str__(self) -> str:
        return self.raw

    def __repr__(self) -> str:
        return f"Version('{self.raw}')"


class Schema(BaseModel):
    """Represents a JSON Schema / OpenAPI Schema object."""

    model_config = {"extra": "allow"}

    title: str | None = None
    type: str | None = None
    description: str | None = None
    properties: dict[str, "Schema"] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    items: "Schema | None" = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Schema":
        """Create a Schema from a dictionary, handling nested schemas."""
        schema_data: dict[str, Any] = {
            "title": data.get("title"),
            "type": data.get("type"),
            "description": data.get("description"),
            "required": data.get("required", []),
        }

        # Handle nested properties
        if "properties" in data:
            schema_data["properties"] = {name: cls.from_dict(prop) for name, prop in data["properties"].items()}

        # Handle array items
        if "items" in data and isinstance(data["items"], dict):
            schema_data["items"] = cls.from_dict(data["items"])

        # Store any additional fields
        for key, value in data.items():
            if key not in schema_data:
                schema_data[key] = value

        return cls(**schema_data)


class Operation(BaseModel):
    """Represents an HTTP operation (GET, POST, etc.)."""

    model_config = {"extra": "allow"}

    method: str
    path: str
    operation_id: str | None = Field(None, alias="operationId")
    summary: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[Any] = Field(default_factory=list)
    responses: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, method: str, path: str, data: Mapping[str, Any]) -> "Operation":
        """Create an Operation from a dictionary."""
        return cls(
            method=method,
            path=path,
            operationId=data.get("operationId"),
            summary=data.get("summary"),
            description=data.get("description"),
            tags=data.get("tags", []),
            parameters=data.get("parameters", []),
            responses=data.get("responses", {}),
            **{k: v for k, v in data.items() if k not in ["operationId", "summary", "description", "tags", "parameters", "responses"]},
        )


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


class Paths(BaseModel):
    """Container for all path items in the spec."""

    model_config = {"extra": "allow"}

    items: dict[str, PathItem] = Field(default_factory=dict)

    def __getitem__(self, path: str) -> PathItem:
        """Get a path item by path string."""
        return self.items[path]

    def __contains__(self, path: str) -> bool:
        """Check if a path exists."""
        return path in self.items

    def all_operations(self) -> Generator[Operation, None, None]:
        """Yield all operations across all paths."""
        for path_item in self.items.values():
            yield from path_item.operations.values()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Paths":
        """Create Paths from a dictionary."""
        items = {}
        for path, path_data in data.items():
            if isinstance(path_data, dict):
                items[path] = PathItem.from_dict(path, path_data)
        return cls(items=items)


class Components(BaseModel):
    """Container for reusable component definitions."""

    model_config = {"extra": "allow"}

    schemas: dict[str, Schema] = Field(default_factory=dict)

    def get(self, schema_name: str) -> Schema | None:
        """Get a schema by name."""
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

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "OpenAPISpec":
        """Create an OpenAPISpec from a dictionary.

        Args:
            data: The OpenAPI/Swagger specification as a dictionary

        Returns:
            OpenAPISpec instance

        Example:
            >>> spec_data = {"openapi": "3.0.0", "paths": {}, "info": {"title": "API"}}
            >>> spec = OpenAPISpec.from_dict(spec_data)
        """
        # Detect version
        version_str = data.get("openapi") or data.get("swagger", "3.0.0")
        version = Version(version_str)

        # Parse paths
        paths_data = data.get("paths", {})
        paths = Paths.from_dict(paths_data)

        # Parse components
        components = Components.from_spec(data, version)

        # Store raw data as regular dict
        raw_dict = dict(data) if not isinstance(data, dict) else data

        return cls(raw=raw_dict, version=version, paths=paths, components=components)

    @classmethod
    def from_json(cls, text: str) -> "OpenAPISpec":
        """Create an OpenAPISpec from a JSON string.

        Args:
            text: JSON string containing the OpenAPI/Swagger specification

        Returns:
            OpenAPISpec instance

        Example:
            >>> json_str = '{"openapi": "3.0.0", "paths": {}, "info": {"title": "API"}}'
            >>> spec = OpenAPISpec.from_json(json_str)
        """
        data = json.loads(text)
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, text: str) -> "OpenAPISpec":
        """Create an OpenAPISpec from a YAML string.

        Args:
            text: YAML string containing the OpenAPI/Swagger specification

        Returns:
            OpenAPISpec instance

        Example:
            >>> yaml_str = '''
            ... openapi: "3.0.0"
            ... paths: {}
            ... info:
            ...   title: API
            ... '''
            >>> spec = OpenAPISpec.from_yaml(yaml_str)
        """
        data = yaml.safe_load(text)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: str | Path) -> "OpenAPISpec":
        """Create an OpenAPISpec from a file.

        Auto-detects format from file extension (.yaml/.yml for YAML, otherwise tries JSON).

        Args:
            path: Path to the OpenAPI/Swagger specification file

        Returns:
            OpenAPISpec instance

        Example:
            >>> spec = OpenAPISpec.from_file("openapi.yaml")
        """
        path_obj = Path(path) if isinstance(path, str) else path
        content = path_obj.read_text()

        # Detect format from extension
        if path_obj.suffix.lower() in [".yaml", ".yml"]:
            return cls.from_yaml(content)
        else:
            # Try JSON first, fall back to YAML
            try:
                return cls.from_json(content)
            except json.JSONDecodeError:
                return cls.from_yaml(content)

    @classmethod
    def from_url(cls, url: str) -> "OpenAPISpec":
        """Create an OpenAPISpec from a URL.

        Detects format from Content-Type header, defaulting to JSON with YAML fallback.

        Args:
            url: URL to fetch the OpenAPI/Swagger specification from

        Returns:
            OpenAPISpec instance

        Example:
            >>> spec = OpenAPISpec.from_url("https://api.example.com/openapi.json")
        """
        request = Request(url)
        with urlopen(request) as response:
            content = response.read().decode("utf-8")
            content_type = response.headers.get("Content-Type", "")

            # Detect format from content-type
            if "yaml" in content_type or "yml" in content_type:
                return cls.from_yaml(content)
            else:
                # Try JSON first, fall back to YAML
                try:
                    return cls.from_json(content)
                except json.JSONDecodeError:
                    return cls.from_yaml(content)

    def operation_by_operation_id(self, operation_id: str) -> Operation | None:
        """Find an operation by its operationId.

        Args:
            operation_id: The operationId to search for

        Returns:
            The Operation if found, None otherwise

        Example:
            >>> spec = OpenAPISpec.from_file("openapi.yaml")
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
            >>> spec = OpenAPISpec.from_file("openapi.yaml")
            >>> for op in spec.all_operations():
            ...     print(op.method, op.path, op.operation_id)
        """
        yield from self.paths.all_operations()
