"""Tests for native OpenAPI 3.1 type-array support on Schema.

OpenAPI 3.1 replaced the 3.0 ``nullable`` keyword with JSON Schema type arrays
(e.g. ``type: ["string", "null"]``). These tests encode the uniform view that
consumers can use without pre-normalizing 3.1 specs to 3.0.
"""

from __future__ import annotations

from cicerone import spec as cicerone_spec
from cicerone.parse import parse_spec_from_dict


class TestTypesProperty:
    """Schema.types is an always-a-list view of the type keyword."""

    def test_single_type(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string"})
        assert schema.types == ["string"]

    def test_type_array(self):
        schema = cicerone_spec.Schema.from_dict({"type": ["string", "null"]})
        assert schema.types == ["string", "null"]

    def test_unset_type(self):
        schema = cicerone_spec.Schema.from_dict({})
        assert schema.types == []


class TestPrimaryTypeProperty:
    """Schema.primary_type is the first non-null type."""

    def test_single_type(self):
        schema = cicerone_spec.Schema.from_dict({"type": "integer"})
        assert schema.primary_type == "integer"

    def test_type_array_with_null(self):
        schema = cicerone_spec.Schema.from_dict({"type": ["string", "null"]})
        assert schema.primary_type == "string"

    def test_null_first_in_array(self):
        schema = cicerone_spec.Schema.from_dict({"type": ["null", "number"]})
        assert schema.primary_type == "number"

    def test_only_null(self):
        schema = cicerone_spec.Schema.from_dict({"type": ["null"]})
        assert schema.primary_type is None

    def test_unset_type(self):
        schema = cicerone_spec.Schema.from_dict({})
        assert schema.primary_type is None


class TestIsNullableProperty:
    """Schema.is_nullable unifies 3.0 nullable and 3.1 type arrays."""

    def test_openapi_30_nullable_keyword(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "nullable": True})
        assert schema.is_nullable is True

    def test_openapi_30_not_nullable(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string"})
        assert schema.is_nullable is False

    def test_openapi_31_type_array_with_null(self):
        schema = cicerone_spec.Schema.from_dict({"type": ["string", "null"]})
        assert schema.is_nullable is True

    def test_openapi_31_type_array_without_null(self):
        schema = cicerone_spec.Schema.from_dict({"type": ["string", "integer"]})
        assert schema.is_nullable is False

    def test_openapi_31_null_only_type(self):
        schema = cicerone_spec.Schema.from_dict({"type": "null"})
        assert schema.is_nullable is True

    def test_any_of_with_null_member(self):
        schema = cicerone_spec.Schema.from_dict({"anyOf": [{"type": "string"}, {"type": "null"}]})
        assert schema.is_nullable is True

    def test_one_of_with_null_member(self):
        schema = cicerone_spec.Schema.from_dict({"oneOf": [{"$ref": "#/components/schemas/User"}, {"type": "null"}]})
        assert schema.is_nullable is True

    def test_composition_without_null_member(self):
        schema = cicerone_spec.Schema.from_dict({"oneOf": [{"type": "string"}, {"type": "integer"}]})
        assert schema.is_nullable is False


class TestEndToEnd31Parsing:
    """A 3.1 spec with type arrays parses without pre-normalization."""

    def test_31_spec_with_type_arrays(self):
        spec = parse_spec_from_dict(
            {
                "openapi": "3.1.0",
                "info": {"title": "Test", "version": "1.0.0"},
                "paths": {},
                "components": {
                    "schemas": {
                        "User": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "nickname": {"type": ["string", "null"]},
                                "age": {"type": ["integer", "null"]},
                            },
                            "required": ["name"],
                        }
                    }
                },
            }
        )
        user = spec.components.schemas["User"]
        assert user.properties["name"].is_nullable is False
        nickname = user.properties["nickname"]
        assert nickname.is_nullable is True
        assert nickname.primary_type == "string"
        age = user.properties["age"]
        assert age.is_nullable is True
        assert age.primary_type == "integer"
