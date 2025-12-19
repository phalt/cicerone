"""Reference model for OpenAPI $ref objects.

References:
- OpenAPI 3.x Reference Object: https://spec.openapis.org/oas/v3.1.0#reference-object
- JSON Reference: https://datatracker.ietf.org/doc/html/draft-pbryan-zyp-json-ref-03
"""

from __future__ import annotations

import typing

import pydantic


class Reference(pydantic.BaseModel):
    """Represents an OpenAPI Reference Object containing a $ref keyword.

    A Reference Object is a simple object to allow referencing other components
    in the OpenAPI document, internally and externally.

    The reference string value ($ref) uses JSON Reference notation and can point to:
    - Local references: #/components/schemas/Pet
    - External file references: ./models/pet.yaml
    - External URL references: https://example.com/schemas/pet.json
    - References with JSON Pointer fragments: ./models.yaml#/Pet

    In OAS 3.1, Reference Objects can also have summary and description fields
    that override those in the referenced object.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    ref: str = pydantic.Field(..., alias="$ref")
    summary: str | None = None  # OAS 3.1+ only
    description: str | None = None  # OAS 3.1+ only

    def __str__(self) -> str:
        """Return a readable string representation of the reference."""
        parts = [f"ref='{self.ref}'"]
        if self.summary:
            parts.append(f"summary='{self.summary[:50]}...'")
        if self.description:
            parts.append(f"description='{self.description[:50]}...'")
        return f"<Reference: {', '.join(parts)}>"

    @property
    def is_local(self) -> bool:
        """Check if this is a local reference (starts with #)."""
        return self.ref.startswith("#")

    @property
    def is_external(self) -> bool:
        """Check if this is an external reference (file or URL)."""
        return not self.is_local

    @property
    def pointer(self) -> str:
        """Get the JSON Pointer part of the reference.

        For local references like '#/components/schemas/User', returns '/components/schemas/User'.
        For external references with fragments like 'file.yaml#/Pet', returns '/Pet'.
        For external references without fragments, returns ''.
        """
        if "#" in self.ref:
            return self.ref.split("#", 1)[1]
        return ""

    @property
    def document(self) -> str:
        """Get the document part of an external reference.

        For external references like './models.yaml#/Pet', returns './models.yaml'.
        For local references, returns empty string.
        """
        if self.is_external:
            if "#" in self.ref:
                return self.ref.split("#", 1)[0]
            return self.ref
        return ""

    @property
    def pointer_parts(self) -> list[str]:
        """Get the JSON Pointer as a list of path components.

        For example, '#/components/schemas/User' returns ['components', 'schemas', 'User'].
        """
        pointer = self.pointer
        if not pointer or pointer == "/":
            return []
        # Remove leading slash and split
        parts = pointer.lstrip("/").split("/")
        # Filter out empty strings
        return [p for p in parts if p]

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Reference:
        """Create a Reference from a dictionary.

        Args:
            data: Dictionary containing at least a '$ref' key

        Returns:
            Reference instance
        """
        return cls(**data)

    @classmethod
    def is_reference(cls, data: typing.Any) -> bool:
        """Check if a data object is a reference (contains '$ref' key).

        Args:
            data: Any data object to check

        Returns:
            True if data is a dict with a '$ref' key
        """
        return isinstance(data, dict) and "$ref" in data
