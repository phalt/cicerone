"""Reference resolution utilities for OpenAPI specifications.

This module provides functionality to resolve $ref references in OpenAPI documents,
supporting both internal references (within the same document) and external references
(to other files or URLs).

References:
- OpenAPI 3.x Reference Resolution: https://spec.openapis.org/oas/v3.1.0#reference-object
- JSON Pointer: https://datatracker.ietf.org/doc/html/rfc6901
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.references import reference as spec_reference
from cicerone.spec import callback as spec_callback
from cicerone.spec import example as spec_example
from cicerone.spec import header as spec_header
from cicerone.spec import link as spec_link
from cicerone.spec import openapi_spec as spec_openapi
from cicerone.spec import parameter as spec_parameter
from cicerone.spec import path_item as spec_path_item
from cicerone.spec import request_body as spec_request_body
from cicerone.spec import response as spec_response
from cicerone.spec import schema as spec_schema
from cicerone.spec import security_scheme as spec_security_scheme

# Map component types to their constructor methods
COMPONENT_TYPE_MAP = {
    "schemas": spec_schema.Schema.from_dict,
    "responses": spec_response.Response.from_dict,
    "parameters": spec_parameter.Parameter.from_dict,
    "examples": spec_example.Example.from_dict,
    "requestBodies": spec_request_body.RequestBody.from_dict,
    "headers": spec_header.Header.from_dict,
    "securitySchemes": spec_security_scheme.SecurityScheme.from_dict,
    "links": spec_link.Link.from_dict,
    "callbacks": spec_callback.Callback.from_dict,
}


class ReferenceResolver:
    """Resolves references in OpenAPI specifications.

    Currently supports internal/local references only (references starting with #).
    External file and URL references are not yet implemented.
    """

    def __init__(self, spec: spec_openapi.OpenAPISpec) -> None:
        """Initialize the reference resolver.

        Args:
            spec: The OpenAPI specification to resolve references in
        """
        self.spec = spec
        self._resolution_stack: list[str] = []

    def resolve_reference(
        self,
        ref: spec_reference.Reference | str,
        follow_nested: bool = True,
    ) -> typing.Any:
        """Resolve a reference to its target object.

        Args:
            ref: Reference object or reference string (e.g., '#/components/schemas/User')
            follow_nested: If True, recursively resolves nested references

        Returns:
            The target object as a typed Pydantic model (Schema, Response, etc.) when
            the reference points to a recognized component type. Otherwise returns raw data.

        Raises:
            ValueError: If the reference cannot be resolved
            RecursionError: If a circular reference is detected

        Example:
            >>> resolver = ReferenceResolver(spec)
            >>> user_schema = resolver.resolve_reference('#/components/schemas/User')
            >>> print(type(user_schema))  # <class 'cicerone.spec.schema.Schema'>
        """
        # Convert string to Reference object if needed
        if isinstance(ref, str):
            ref = spec_reference.Reference(ref=ref)

        # Check for circular references
        if ref.ref in self._resolution_stack:
            raise RecursionError(f"Circular reference detected: {' -> '.join(self._resolution_stack + [ref.ref])}")

        # Add to resolution stack for circular reference detection
        self._resolution_stack.append(ref.ref)

        try:
            # Currently only support local references
            if ref.is_external:
                raise ValueError(f"External references are not yet supported: {ref.ref}")

            # Resolve local reference
            target = self._resolve_local_reference(ref)

            # If the target is itself a reference and we should follow it
            if follow_nested and spec_reference.Reference.is_reference(target):
                nested_ref = spec_reference.Reference.from_dict(target)
                return self.resolve_reference(nested_ref, follow_nested=True)

            # If follow_nested is True and target is a typed object, resolve nested $refs
            if follow_nested and not isinstance(target, dict):
                target = self._resolve_nested_references(target)

            return target

        finally:
            # Remove from resolution stack
            self._resolution_stack.pop()

    def _resolve_local_reference(self, ref: spec_reference.Reference) -> typing.Any:
        """Resolve a local reference (starting with #).

        Args:
            ref: Reference object with a local reference string

        Returns:
            The target object as a typed Pydantic model when possible

        Raises:
            ValueError: If the reference path is invalid or not found
        """
        if not ref.is_local:
            raise ValueError(f"Expected local reference, got: {ref.ref}")

        if not ref.pointer_parts:
            # Reference to the root document
            return self.spec.raw

        # Navigate through the spec using the pointer path
        current = self.spec.raw
        for i, part in enumerate(ref.pointer_parts):
            path_so_far = "/" + "/".join(ref.pointer_parts[: i + 1])
            try:
                current = current[int(part)] if isinstance(current, list) else current[part]
            except (KeyError, IndexError, ValueError) as e:
                raise ValueError(f"Reference path not found: {ref.ref} (failed at {path_so_far})") from e
            except TypeError as e:
                raise ValueError(
                    f"Cannot navigate through non-dict/list object: {ref.ref} (failed at {path_so_far})"
                ) from e

        # Convert the raw dict to a typed object based on the reference path
        return self._convert_to_typed_object(ref, current)

    def _convert_to_typed_object(self, ref: spec_reference.Reference, data: typing.Any) -> typing.Any:
        """Convert raw data to a typed Pydantic object based on the reference path.

        Args:
            ref: Reference object containing the path
            data: Raw data to convert

        Returns:
            Typed Pydantic object if the path is recognized, otherwise raw data
        """
        # Don't convert if the data itself is a reference (has $ref key)
        if isinstance(data, dict) and "$ref" in data:
            return data

        parts = ref.pointer_parts
        if len(parts) < 2:
            return data

        # Map component types to their constructors
        if parts[0] == "components" and len(parts) >= 3:
            if constructor := COMPONENT_TYPE_MAP.get(parts[1]):
                return constructor(data)

        # Map paths to PathItem objects
        if parts[0] == "paths" and len(parts) >= 2:
            path = "/" + "/".join(parts[1:])  # Reconstruct the path
            return spec_path_item.PathItem.from_dict(path, data)

        # If we can't determine the type, return raw data
        return data

    def _resolve_nested_references(self, obj: typing.Any) -> typing.Any:
        """Recursively resolve any $ref fields within a typed object.

        Args:
            obj: A typed Pydantic object (Schema, Response, etc.)

        Returns:
            The same object with nested $refs resolved to their target objects
        """
        if not isinstance(obj, pydantic.BaseModel):
            return obj

        # Iterate through model fields and resolve any references
        for field_name, field_value in obj:
            if field_value is None:
                continue

            match field_value:
                case pydantic.BaseModel():
                    self._resolve_model_field(obj, field_name, field_value)
                case dict():
                    self._resolve_container(field_value)
                case list():
                    self._resolve_container(field_value)

        return obj

    def _get_ref_from_model(self, model: pydantic.BaseModel) -> str | None:
        """Extract $ref from a Pydantic model's extra fields if present.

        Args:
            model: Pydantic model to check

        Returns:
            The $ref string if found, None otherwise
        """
        return getattr(model, "__pydantic_extra__", {}).get("$ref")

    def _try_resolve_ref(self, ref: str) -> typing.Any | None:
        """Attempt to resolve a reference, returning None on failure.

        Args:
            ref: Reference string to resolve

        Returns:
            Resolved object or None if resolution fails
        """
        try:
            return self.resolve_reference(ref, follow_nested=True)
        except (ValueError, RecursionError):
            return None

    def _resolve_model_or_recurse(self, model: pydantic.BaseModel) -> typing.Any:
        """Resolve a model's $ref or recursively resolve its nested references.

        Args:
            model: Pydantic model to process

        Returns:
            Resolved object if $ref found, otherwise the model with nested refs resolved
        """
        if ref := self._get_ref_from_model(model):
            if resolved := self._try_resolve_ref(ref):
                return resolved
        return self._resolve_nested_references(model)

    def _resolve_model_field(
        self, parent_obj: pydantic.BaseModel, field_name: str, field_value: pydantic.BaseModel
    ) -> None:
        """Resolve a Pydantic model field that may contain a $ref.

        Args:
            parent_obj: The parent object containing this field
            field_name: Name of the field being resolved
            field_value: The Pydantic model value to check for $ref
        """
        parent_obj.__dict__[field_name] = self._resolve_model_or_recurse(field_value)

    def _resolve_container(self, container: dict | list) -> None:
        """Resolve references in dictionary or list containers.

        Args:
            container: Dictionary or list to process
        """
        items = container.items() if isinstance(container, dict) else enumerate(container)

        for key, value in items:
            if isinstance(value, pydantic.BaseModel):
                container[key] = self._resolve_model_or_recurse(value)

    def get_all_references(
        self,
        obj: typing.Any | None = None,
        visited: set[int] | None = None,
    ) -> dict[str, spec_reference.Reference]:
        """Find all references in an object or the entire spec.

        Recursively searches for all $ref keywords in the given object or the entire spec.

        Args:
            obj: Object to search for references (defaults to entire spec)
            visited: Set of object ids already visited (for circular reference handling)

        Returns:
            Dictionary mapping $ref strings to Reference objects

        Example:
            >>> resolver = ReferenceResolver(spec)
            >>> all_refs = resolver.get_all_references()
            >>> # Access by reference string
            >>> user_ref = all_refs.get('#/components/schemas/User')
            >>> # Get all local references
            >>> local_refs = {k: v for k, v in all_refs.items() if v.is_local}
        """
        obj = obj or self.spec.raw
        visited = visited or set()

        # Avoid infinite recursion on circular structures
        if (obj_id := id(obj)) in visited:
            return {}
        visited.add(obj_id)

        references = {}

        # Check if this object is a reference
        if spec_reference.Reference.is_reference(obj):
            ref = spec_reference.Reference.from_dict(obj)
            references[ref.ref] = ref

        # Recursively search through collections
        match obj:
            case dict():
                for value in obj.values():
                    references.update(self.get_all_references(value, visited))
            case list():
                for item in obj:
                    references.update(self.get_all_references(item, visited))

        return references

    def is_circular_reference(self, ref: spec_reference.Reference | str) -> bool:
        """Check if resolving a reference would create a circular dependency.

        Args:
            ref: Reference to check

        Returns:
            True if the reference is circular

        Example:
            >>> resolver = ReferenceResolver(spec)
            >>> if resolver.is_circular_reference('#/components/schemas/Node'):
            ...     print("This schema has a circular reference")
        """
        # Convert string to Reference if needed
        if isinstance(ref, str):
            ref = spec_reference.Reference(ref=ref)

        try:
            self.resolve_reference(ref, follow_nested=True)
            return False
        except RecursionError:
            return True
