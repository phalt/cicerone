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

from cicerone.spec import reference as spec_reference

if typing.TYPE_CHECKING:
    from cicerone.spec import openapi_spec as spec_openapi


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
            The target object that the reference points to

        Raises:
            ValueError: If the reference cannot be resolved
            RecursionError: If a circular reference is detected

        Example:
            >>> resolver = ReferenceResolver(spec)
            >>> user_schema = resolver.resolve_reference('#/components/schemas/User')
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

            return target

        finally:
            # Remove from resolution stack
            self._resolution_stack.pop()

    def _resolve_local_reference(self, ref: spec_reference.Reference) -> typing.Any:
        """Resolve a local reference (starting with #).

        Args:
            ref: Reference object with a local reference string

        Returns:
            The target object

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

        return current

    def get_all_references(
        self,
        obj: typing.Any | None = None,
        visited: set[int] | None = None,
    ) -> list[spec_reference.Reference]:
        """Find all references in an object or the entire spec.

        Recursively searches for all $ref keywords in the given object or the entire spec.

        Args:
            obj: Object to search for references (defaults to entire spec)
            visited: Set of object ids already visited (for circular reference handling)

        Returns:
            List of all Reference objects found

        Example:
            >>> resolver = ReferenceResolver(spec)
            >>> all_refs = resolver.get_all_references()
            >>> local_refs = [r for r in all_refs if r.is_local]
        """
        if obj is None:
            obj = self.spec.raw

        if visited is None:
            visited = set()

        # Avoid infinite recursion on circular structures
        obj_id = id(obj)
        if obj_id in visited:
            return []
        visited.add(obj_id)

        references: list[spec_reference.Reference] = []

        if spec_reference.Reference.is_reference(obj):
            references.append(spec_reference.Reference.from_dict(obj))

        if isinstance(obj, dict):
            for value in obj.values():
                references.extend(self.get_all_references(value, visited))
        elif isinstance(obj, list):
            for item in obj:
                references.extend(self.get_all_references(item, visited))

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
