"""Reference model for OpenAPI $ref objects.

References:
- OpenAPI 3.x Reference Object: https://spec.openapis.org/oas/v3.1.0#reference-object
- JSON Reference: https://datatracker.ietf.org/doc/html/draft-pbryan-zyp-json-ref-03
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils


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

    model_config = {"extra": "allow"}

    ref: str
    summary: str | None = None
    description: str | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def handle_dollar_ref(cls, data: typing.Any) -> typing.Any:
        """Handle $ref in input data by converting it to ref.

        This allows accepting both ref= and $ref in dictionaries.
        """
        if isinstance(data, dict) and "$ref" in data:
            data = data.copy()
            data["ref"] = data.pop("$ref")
        return data

    def model_dump(self, **kwargs) -> dict[str, typing.Any]:
        """Serialize with $ref instead of ref."""
        result = super().model_dump(**kwargs)
        if "ref" in result:
            result["$ref"] = result.pop("ref")
        return result

    def __str__(self) -> str:
        """Return a readable string representation of the reference."""
        parts = [f"ref='{self.ref}'"]
        if self.summary:
            parts.append(f"summary='{model_utils.truncate_text(self.summary)}'")
        if self.description:
            parts.append(f"description='{model_utils.truncate_text(self.description)}'")
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
        return self.ref.split("#", 1)[1] if "#" in self.ref else ""

    @property
    def document(self) -> str:
        """Get the document part of an external reference.

        For external references like './models.yaml#/Pet', returns './models.yaml'.
        For local references, returns empty string.
        """
        if self.is_external:
            return self.ref.split("#", 1)[0] if "#" in self.ref else self.ref
        return ""

    @property
    def pointer_parts(self) -> list[str]:
        """Get the JSON Pointer as a list of path components.

        For example, '#/components/schemas/User' returns ['components', 'schemas', 'User'].
        """
        pointer = self.pointer
        if not pointer or pointer == "/":
            return []
        return [p for p in pointer.lstrip("/").split("/") if p]

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Reference:
        """Create a Reference from a dictionary.

        Args:
            data: Dictionary containing at least a '$ref' key

        Returns:
            Reference instance

        Raises:
            ValueError: If '$ref' key is not present in data
        """
        if "$ref" not in data:
            raise ValueError("Reference dictionary must contain a '$ref' key")
        return cls(**data)

    @classmethod
    def is_reference(cls, data: typing.Any) -> bool:
        """Check if a data object is a reference.

        According to OpenAPI spec, a Reference Object MUST contain a $ref field.
        Any other fields are ignored (except summary/description in OAS 3.1+).

        Args:
            data: Any data object to check

        Returns:
            True if data is a dict with a '$ref' key
        """
        return isinstance(data, dict) and "$ref" in data
