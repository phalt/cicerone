"""Tests for Schema model."""

from cicerone.spec.schema import Schema


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
        schema = Schema.from_dict(data)
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
        schema = Schema.from_dict(data)
        assert "user" in schema.properties
        assert schema.properties["user"].type == "object"
        assert "name" in schema.properties["user"].properties

    def test_array_schema(self):
        """Test creating a schema with array items."""
        data = {"type": "array", "items": {"type": "string"}}
        schema = Schema.from_dict(data)
        assert schema.type == "array"
        assert schema.items is not None
        assert schema.items.type == "string"
