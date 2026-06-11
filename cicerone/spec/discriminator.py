"""Discriminator model for OpenAPI discriminator objects.

References:
- OpenAPI 3.x Discriminator Object: https://spec.openapis.org/oas/v3.1.0#discriminator-object
"""

from __future__ import annotations

import typing

import pydantic


class Discriminator(pydantic.BaseModel):
    """Represents an OpenAPI Discriminator Object.

    Used with oneOf/anyOf/allOf composition to hint which schema a payload
    matches, based on the value of a named property.
    """

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow", "populate_by_name": True}

    property_name: str = pydantic.Field(alias="propertyName")
    mapping: dict[str, str] = pydantic.Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of the discriminator."""
        parts = [f"propertyName={self.property_name}"]
        if self.mapping:
            parts.append(f"{len(self.mapping)} mappings")
        return f"<Discriminator: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Discriminator:
        """Create a Discriminator from a dictionary."""
        return cls(**data)
