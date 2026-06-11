"""Schema model for JSON Schema / OpenAPI Schema objects.

References:
- OpenAPI 3.x Schema Object: https://spec.openapis.org/oas/v3.1.0#schema-object
- JSON Schema: https://json-schema.org/specification
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import discriminator as spec_discriminator
from cicerone.spec import model_utils


class Schema(model_utils.SpecModel):
    """Represents a JSON Schema / OpenAPI Schema object.

    Extra fields are allowed to support the full JSON Schema vocabulary and
    vendor extensions.
    """

    # Keys whose values are themselves schemas (or schema containers) and need
    # recursive parsing in from_dict() rather than plain Pydantic validation
    NESTED_SCHEMA_KEYS: typing.ClassVar[set[str]] = {
        "properties",
        "items",
        "allOf",
        "oneOf",
        "anyOf",
        "not",
        "additionalProperties",
        "discriminator",
    }

    # Keys promoted to typed fields in 0.4.0 that are still mirrored into
    # model_extra for backwards compatibility (removed in 0.5.0)
    MIRRORED_EXTRA_KEYS: typing.ClassVar[tuple[str, ...]] = (
        "$ref",
        "format",
        "enum",
        "default",
        "const",
        "deprecated",
        "nullable",
        "readOnly",
        "writeOnly",
        "discriminator",
        "additionalProperties",
        "example",
        "examples",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "minLength",
        "maxLength",
        "pattern",
        "minItems",
        "maxItems",
        "uniqueItems",
        "minProperties",
        "maxProperties",
    )

    ref: str | None = pydantic.Field(None, alias="$ref")
    title: str | None = None
    type: str | list[str] | None = None
    format: str | None = None
    description: str | None = None
    properties: dict[str, Schema] = pydantic.Field(default_factory=dict)
    required: list[str] = pydantic.Field(default_factory=list)
    items: Schema | None = None
    # Value keywords
    enum: list[typing.Any] | None = None
    default: typing.Any = None
    const: typing.Any = None
    example: typing.Any = None
    # JSON Schema uses a list for `examples`; some real-world 3.0 specs use a dict
    examples: list[typing.Any] | dict[str, typing.Any] | None = None
    # Metadata keywords
    deprecated: bool = False
    nullable: bool | None = None  # OpenAPI 3.0 keyword (3.1 uses type arrays)
    read_only: bool | None = pydantic.Field(None, alias="readOnly")
    write_only: bool | None = pydantic.Field(None, alias="writeOnly")
    # Composition keywords
    all_of: list[Schema] | None = pydantic.Field(None, alias="allOf")
    one_of: list[Schema] | None = pydantic.Field(None, alias="oneOf")
    any_of: list[Schema] | None = pydantic.Field(None, alias="anyOf")
    not_: Schema | None = pydantic.Field(None, alias="not")
    discriminator: spec_discriminator.Discriminator | None = None
    additional_properties: Schema | bool | None = pydantic.Field(None, alias="additionalProperties")
    # Numeric constraints (exclusiveMinimum/Maximum are bool in 3.0, number in 3.1)
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: bool | float | None = pydantic.Field(None, alias="exclusiveMinimum")
    exclusive_maximum: bool | float | None = pydantic.Field(None, alias="exclusiveMaximum")
    multiple_of: float | None = pydantic.Field(None, alias="multipleOf")
    # String constraints
    min_length: int | None = pydantic.Field(None, alias="minLength")
    max_length: int | None = pydantic.Field(None, alias="maxLength")
    pattern: str | None = None
    # Array constraints
    min_items: int | None = pydantic.Field(None, alias="minItems")
    max_items: int | None = pydantic.Field(None, alias="maxItems")
    unique_items: bool | None = pydantic.Field(None, alias="uniqueItems")
    # Object constraints
    min_properties: int | None = pydantic.Field(None, alias="minProperties")
    max_properties: int | None = pydantic.Field(None, alias="maxProperties")

    def __str__(self) -> str:
        """Return a readable string representation of the schema."""
        parts = []
        if self.ref:
            parts.append(f"ref={self.ref}")
        if self.title:
            parts.append(f"'{self.title}'")
        if self.type:
            parts.append(f"type={self.type}")
        if self.enum:
            parts.append(f"enum[{len(self.enum)}]")
        if self.properties:
            parts.append(f"{len(self.properties)} properties")
        if self.required:
            parts.append(f"required={self.required}")
        if self.items:
            parts.append(f"items={self.items.type or 'object'}")

        content = ", ".join(parts) if parts else "empty schema"
        return f"<Schema: {content}>"

    @property
    def types(self) -> list[str]:
        """Always-a-list view of the ``type`` keyword.

        OpenAPI 3.1 allows type arrays (``type: ["string", "null"]``) while 3.0
        only allows a single string. This property unifies both forms; it returns
        an empty list when ``type`` is unset.
        """
        if self.type is None:
            return []
        if isinstance(self.type, str):
            return [self.type]
        return list(self.type)

    @property
    def primary_type(self) -> str | None:
        """The first non-``"null"`` type, or None if there isn't one."""
        return next((t for t in self.types if t != "null"), None)

    @property
    def is_nullable(self) -> bool:
        """True if the schema accepts null values.

        Unifies the OpenAPI 3.0 ``nullable`` keyword, OpenAPI 3.1 type arrays
        containing ``"null"``, and anyOf/oneOf compositions with a
        ``{"type": "null"}`` member.
        """
        if self.nullable:
            return True
        if "null" in self.types:
            return True
        for members in (self.any_of, self.one_of):
            if members and any("null" in member.types for member in members):
                return True
        return False

    @property
    def has_default(self) -> bool:
        """True if the schema explicitly declares a default (including ``default: null``)."""
        return "default" in self.model_fields_set

    @property
    def has_const(self) -> bool:
        """True if the schema explicitly declares a const (including ``const: null``)."""
        return "const" in self.model_fields_set

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Schema:
        """Create a Schema from a dictionary, handling nested schemas."""
        # All scalar fields resolve via Pydantic aliases when the raw keys are
        # splatted; only schema-valued keys need recursive parsing
        kwargs: dict[str, typing.Any] = {k: v for k, v in data.items() if k not in cls.NESTED_SCHEMA_KEYS}

        kwargs["properties"] = model_utils.parse_collection(data, "properties", cls.from_dict)
        # JSON Schema allows boolean schemas (true/false); only parse dict values
        items = data.get("items")
        if isinstance(items, dict):
            kwargs["items"] = cls.from_dict(items)
        for key in ("allOf", "oneOf", "anyOf"):
            parsed = model_utils.parse_list_or_none(data, key, cls.from_dict)
            if parsed is not None:
                kwargs[key] = parsed
        not_value = data.get("not")
        if isinstance(not_value, dict):
            kwargs["not"] = cls.from_dict(not_value)
        additional = data.get("additionalProperties")
        if isinstance(additional, dict):
            kwargs["additionalProperties"] = cls.from_dict(additional)
        elif isinstance(additional, bool):
            kwargs["additionalProperties"] = additional
        discriminator_value = data.get("discriminator")
        if isinstance(discriminator_value, dict):
            kwargs["discriminator"] = spec_discriminator.Discriminator.from_dict(discriminator_value)

        schema = cls(**kwargs)
        model_utils.mirror_extras(schema, data, cls.MIRRORED_EXTRA_KEYS)
        return schema
