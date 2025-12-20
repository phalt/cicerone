"""Top-level OpenAPISpec model.

References:
- OpenAPI 3.x Specification: https://spec.openapis.org/oas/v3.1.0
"""

from __future__ import annotations

import itertools
import typing

import pydantic

from cicerone.references import reference as spec_reference
from cicerone.references import reference_resolver as spec_reference_resolver
from cicerone.spec import components as spec_components
from cicerone.spec import info as spec_info
from cicerone.spec import operation as spec_operation
from cicerone.spec import paths as spec_paths
from cicerone.spec import server as spec_server
from cicerone.spec import tag as spec_tag
from cicerone.spec import version as spec_version
from cicerone.spec import webhooks as spec_webhooks


class OpenAPISpec(pydantic.BaseModel):
    """Top-level OpenAPI specification model."""

    # Model configuration:
    # - extra="allow": Supports vendor extensions (x-* fields) and preserves all spec data
    # - arbitrary_types_allowed=True: Required for the custom Version class (non-Pydantic)
    model_config = {"extra": "allow", "arbitrary_types_allowed": True}

    raw: dict[str, typing.Any]
    version: spec_version.Version
    info: spec_info.Info | None = None
    json_schema_dialect: str | None = pydantic.Field(None, alias="jsonSchemaDialect")
    servers: list[spec_server.Server] = pydantic.Field(default_factory=list)
    paths: spec_paths.Paths
    webhooks: spec_webhooks.Webhooks = pydantic.Field(default_factory=lambda: spec_webhooks.Webhooks(items={}))
    components: spec_components.Components
    security: list[dict[str, list[str]]] = pydantic.Field(default_factory=list)
    tags: list[spec_tag.Tag] = pydantic.Field(default_factory=list)
    external_docs: spec_tag.ExternalDocumentation | None = pydantic.Field(None, alias="externalDocs")

    def __str__(self) -> str:
        """Return a readable string representation of the OpenAPI spec."""
        title = self.raw.get("info", {}).get("title", "Untitled")
        num_paths = len(self.paths.items)
        num_schemas = len(self.components.schemas)
        return f"<OpenAPISpec: '{title}' v{self.version}, {num_paths} paths, {num_schemas} schemas>"

    def operation_by_operation_id(self, operation_id: str) -> spec_operation.Operation | None:
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

    def all_operations(self) -> typing.Generator[spec_operation.Operation, None, None]:
        """Yield all operations in the spec (from paths and webhooks).

        Yields:
            Operation objects

        Example:
            >>> from cicerone.parse import parse_spec_from_file
            >>> spec = parse_spec_from_file("openapi.yaml")
            >>> for op in spec.all_operations():
            ...     print(op.method, op.path, op.operation_id)
        """
        yield from itertools.chain(self.paths.all_operations(), self.webhooks.all_operations())

    def resolve_reference(
        self,
        ref: spec_reference.Reference | str,
        follow_nested: bool = True,
    ) -> typing.Any:
        """Resolve a reference to its target object.

        This method resolves $ref references in the OpenAPI specification,
        supporting both local references (within this document) and following
        chains of nested references.

        Args:
            ref: Reference object or reference string (e.g., '#/components/schemas/User')
            follow_nested: If True, recursively resolves nested references

        Returns:
            The target object as a typed Pydantic model (Schema, Response, Parameter, etc.)
            when the reference points to a recognized component type. Otherwise returns raw data.

        Raises:
            ValueError: If the reference cannot be resolved
            RecursionError: If a circular reference is detected

        Example:
            >>> from cicerone.parse import parse_spec_from_file
            >>> spec = parse_spec_from_file("openapi.yaml")
            >>> user_schema = spec.resolve_reference('#/components/schemas/User')
            >>> # Returns a Schema object, not a dict
            >>> print(type(user_schema))  # <class 'cicerone.spec.schema.Schema'>
        """
        resolver = spec_reference_resolver.ReferenceResolver(self)
        return resolver.resolve_reference(ref, follow_nested=follow_nested)

    def get_all_references(self) -> dict[str, spec_reference.Reference]:
        """Get all references in the specification.

        Recursively searches the entire OpenAPI specification for all $ref keywords
        and returns them as a dictionary mapping reference strings to Reference objects.

        Returns:
            Dictionary mapping $ref strings to Reference objects

        Example:
            >>> from cicerone.parse import parse_spec_from_file
            >>> spec = parse_spec_from_file("openapi.yaml")
            >>> all_refs = spec.get_all_references()
            >>> # Access by reference string
            >>> user_ref = all_refs.get('#/components/schemas/User')
            >>> # Get all local references
            >>> local_refs = {k: v for k, v in all_refs.items() if v.is_local}
            >>> print(f"Found {len(all_refs)} references")
        """
        resolver = spec_reference_resolver.ReferenceResolver(self)
        return resolver.get_all_references()
