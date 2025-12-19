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


class ReferenceResolver:
    """Resolves references in OpenAPI specifications.

    This class provides methods to resolve both internal and external references,
    navigate the reference graph, and detect circular references.
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
            >>> # Returns a Schema object, not a dict
            >>> print(type(user_schema))  # <class 'cicerone.spec.schema.Schema'>
        """
        # Convert string to Reference object if needed
        if isinstance(ref, str):
            ref = spec_reference.Reference(**{"$ref": ref})

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

        parts = ref.pointer_parts
        if not parts:
            # Reference to the root document
            return self.spec.raw

        # Navigate through the spec using the pointer path
        current = self.spec.raw
        for i, part in enumerate(parts):
            if isinstance(current, dict):
                if part not in current:
                    path_so_far = "/" + "/".join(parts[: i + 1])
                    raise ValueError(f"Reference path not found: {ref.ref} (failed at {path_so_far})")
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError) as e:
                    path_so_far = "/" + "/".join(parts[: i + 1])
                    raise ValueError(f"Invalid array index in reference: {ref.ref} (failed at {path_so_far})") from e
            else:
                path_so_far = "/" + "/".join(parts[: i + 1])
                raise ValueError(f"Cannot navigate through non-dict/list object: {ref.ref} (failed at {path_so_far})")

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

        if not isinstance(data, dict):
            return data

        parts = ref.pointer_parts
        if len(parts) < 2:
            return data

        # Map component types to their constructors
        if parts[0] == "components" and len(parts) >= 3:
            component_type = parts[1]
            match component_type:
                case "schemas":
                    return spec_schema.Schema.from_dict(data)
                case "responses":
                    return spec_response.Response.from_dict(data)
                case "parameters":
                    return spec_parameter.Parameter.from_dict(data)
                case "examples":
                    return spec_example.Example.from_dict(data)
                case "requestBodies":
                    return spec_request_body.RequestBody.from_dict(data)
                case "headers":
                    return spec_header.Header.from_dict(data)
                case "securitySchemes":
                    return spec_security_scheme.SecurityScheme.from_dict(data)
                case "links":
                    return spec_link.Link.from_dict(data)
                case "callbacks":
                    return spec_callback.Callback.from_dict(data)

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

        # Get the model's fields
        for field_name, field_value in obj:
            if field_value is None:
                continue

            # Check if this field contains a $ref
            if isinstance(field_value, pydantic.BaseModel):
                # Check if the model has a $ref in its extra fields
                extra_fields = getattr(field_value, "__pydantic_extra__", {})
                if "$ref" in extra_fields:
                    # Resolve the reference
                    try:
                        resolved = self.resolve_reference(extra_fields["$ref"], follow_nested=True)
                        # Update the field with the resolved object
                        setattr(obj, field_name, resolved)
                    except (ValueError, RecursionError):
                        # If we can't resolve, keep the original
                        pass
                else:
                    # Recursively process nested objects
                    setattr(obj, field_name, self._resolve_nested_references(field_value))

            elif isinstance(field_value, dict):
                # Process dictionary values
                for key, value in field_value.items():
                    if isinstance(value, pydantic.BaseModel):
                        extra_fields = getattr(value, "__pydantic_extra__", {})
                        if "$ref" in extra_fields:
                            try:
                                resolved = self.resolve_reference(extra_fields["$ref"], follow_nested=True)
                                field_value[key] = resolved
                            except (ValueError, RecursionError):
                                pass
                        else:
                            field_value[key] = self._resolve_nested_references(value)

            elif isinstance(field_value, list):
                # Process list items
                for i, item in enumerate(field_value):
                    if isinstance(item, pydantic.BaseModel):
                        extra_fields = getattr(item, "__pydantic_extra__", {})
                        if "$ref" in extra_fields:
                            try:
                                resolved = self.resolve_reference(extra_fields["$ref"], follow_nested=True)
                                field_value[i] = resolved
                            except (ValueError, RecursionError):
                                pass
                        else:
                            field_value[i] = self._resolve_nested_references(item)

        return obj

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
        if obj is None:
            obj = self.spec.raw

        if visited is None:
            visited = set()

        # Avoid infinite recursion on circular structures
        obj_id = id(obj)
        if obj_id in visited:
            return {}
        visited.add(obj_id)

        references: dict[str, spec_reference.Reference] = {}

        if spec_reference.Reference.is_reference(obj):
            ref = spec_reference.Reference.from_dict(obj)
            references[ref.ref] = ref

        if isinstance(obj, dict):
            for value in obj.values():
                references.update(self.get_all_references(value, visited))
        elif isinstance(obj, list):
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
            ref = spec_reference.Reference(**{"$ref": ref})

        try:
            self.resolve_reference(ref, follow_nested=True)
            return False
        except RecursionError:
            return True
