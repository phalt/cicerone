"""Tests for Components container."""

from cicerone.spec.components import Components
from cicerone.spec.version import Version


class TestComponents:
    """Tests for Components container."""

    def test_components_openapi3(self):
        """Test creating Components from OpenAPI 3.x spec."""
        raw = {
            "openapi": "3.0.0",
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {"id": {"type": "string"}},
                    },
                },
            },
        }
        version = Version("3.0.0")
        components = Components.from_spec(raw, version)
        assert "User" in components.schemas
        user_schema = components.get_schema("User")
        assert user_schema is not None
        assert user_schema.type == "object"

    def test_components_swagger2(self):
        """Test creating Components from Swagger 2.0 spec."""
        raw = {
            "swagger": "2.0",
            "definitions": {
                "Pet": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                },
            },
        }
        version = Version("2.0")
        components = Components.from_spec(raw, version)
        assert "Pet" in components.schemas
        assert components.get_schema("Pet") is not None
