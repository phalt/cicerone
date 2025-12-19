"""Tests for Schema model."""

from __future__ import annotations

from cicerone import spec as cicerone_spec


class TestSchema:
    """Tests for Schema model."""

    def test_basic_schema(self):
        """Test creating a basic schema."""
        data = {
            "type": "object",
            "title": "User",
            "description": "A user object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        schema = cicerone_spec.Schema.from_dict(data)
        assert schema.type == "object"
        assert schema.title == "User"
        assert schema.description == "A user object"
        assert schema.required == ["id", "name"]
        assert "id" in schema.properties
        assert schema.properties["id"].type == "string"
        assert schema.properties["name"].type == "string"
        assert schema.properties["age"].type == "integer"

    def test_nested_schema(self):
        """Test creating a schema with nested objects."""
        data = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
            },
        }
        schema = cicerone_spec.Schema.from_dict(data)
        assert "user" in schema.properties
        assert schema.properties["user"].type == "object"
        assert "name" in schema.properties["user"].properties

    def test_array_schema(self):
        """Test creating a schema with array items."""
        data = {"type": "array", "items": {"type": "string"}}
        schema = cicerone_spec.Schema.from_dict(data)
        assert schema.type == "array"
        assert schema.items is not None
        assert schema.items.type == "string"

    def test_schema_str_representation(self):
        """Test __str__ method of Schema."""
        data = {
            "type": "object",
            "title": "User",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
            },
            "required": ["id", "name"],
        }
        schema = cicerone_spec.Schema.from_dict(data)
        str_repr = str(schema)
        assert "<Schema:" in str_repr
        assert "'User'" in str_repr
        assert "type=object" in str_repr
        assert "2 properties" in str_repr
        assert "required=['id', 'name']" in str_repr

    def test_schema_str_array_type(self):
        """Test __str__ method for array schema."""
        data = {"type": "array", "items": {"type": "string"}}
        schema = cicerone_spec.Schema.from_dict(data)
        str_repr = str(schema)
        assert "type=array" in str_repr
        assert "items=string" in str_repr

    def test_schema_str_empty(self):
        """Test __str__ method for empty schema."""
        data: dict[str, str] = {}
        schema = cicerone_spec.Schema.from_dict(data)
        str_repr = str(schema)
        assert "empty schema" in str_repr
