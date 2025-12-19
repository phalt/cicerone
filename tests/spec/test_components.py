"""Tests for Components container."""

from __future__ import annotations

from cicerone import spec as cicerone_spec


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
        components = cicerone_spec.Components.from_spec(raw)
        assert "User" in components.schemas
        user_schema = components.get_schema("User")
        assert user_schema is not None
        assert user_schema.type == "object"

    def test_components_with_all_types_openapi3(self):
        """Test creating Components with all component types from OpenAPI 3.x spec."""
        raw = {
            "openapi": "3.0.0",
            "components": {
                "schemas": {
                    "User": {"type": "object"},
                },
                "responses": {
                    "NotFound": {"description": "Not found"},
                },
                "parameters": {
                    "PageParam": {"name": "page", "in": "query"},
                },
                "examples": {
                    "UserExample": {"value": {"id": "123"}},
                },
                "requestBodies": {
                    "UserBody": {"description": "User request body"},
                },
                "headers": {
                    "RateLimit": {"description": "Rate limit header"},
                },
                "securitySchemes": {
                    "ApiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                },
                "links": {
                    "UserLink": {"operationId": "getUser"},
                },
                "callbacks": {
                    "WebhookCallback": {"expression": "http://example.com"},
                },
            },
        }
        components = cicerone_spec.Components.from_spec(raw)

        # Verify all component types are parsed
        assert len(components.schemas) == 1
        assert len(components.responses) == 1
        assert len(components.parameters) == 1
        assert len(components.examples) == 1
        assert len(components.request_bodies) == 1
        assert len(components.headers) == 1
        assert len(components.security_schemes) == 1
        assert len(components.links) == 1
        assert len(components.callbacks) == 1

        # Verify content
        assert "User" in components.schemas
        assert "NotFound" in components.responses
        assert "PageParam" in components.parameters
        assert "UserExample" in components.examples
        assert "UserBody" in components.request_bodies
        assert "RateLimit" in components.headers
        assert "ApiKey" in components.security_schemes
        assert "UserLink" in components.links
        assert "WebhookCallback" in components.callbacks

    def test_components_str_representation_empty(self):
        """Test __str__ method for empty components."""
        components = cicerone_spec.Components()
        str_repr = str(components)
        assert "<Components: empty>" in str_repr

    def test_components_str_representation_with_schemas(self):
        """Test __str__ method with schemas."""
        raw = {
            "openapi": "3.0.0",
            "components": {
                "schemas": {
                    "User": {"type": "object"},
                    "Post": {"type": "object"},
                },
            },
        }
        components = cicerone_spec.Components.from_spec(raw)
        str_repr = str(components)
        assert "<Components:" in str_repr
        assert "2 schemas" in str_repr

    def test_components_str_representation_multiple_types(self):
        """Test __str__ method with multiple component types."""
        raw = {
            "openapi": "3.0.0",
            "components": {
                "schemas": {"User": {"type": "object"}},
                "responses": {"NotFound": {"description": "Not found"}},
                "parameters": {"PageParam": {"name": "page", "in": "query"}},
                "examples": {"Ex1": {"value": "test"}},
                "requestBodies": {"Body1": {"description": "test"}},
            },
        }
        components = cicerone_spec.Components.from_spec(raw)
        str_repr = str(components)
        assert "<Components:" in str_repr
        # Should show first 3 types and indicate more
        assert "(+2 more types)" in str_repr

    def test_components_str_with_headers_links_callbacks(self):
        """Test __str__ method includes headers, links, and callbacks."""
        raw = {
            "openapi": "3.0.0",
            "components": {
                "headers": {"X-Rate-Limit": {"description": "Rate limit"}},
                "links": {"UserLink": {"operationId": "getUser"}},
                "callbacks": {"WebhookCallback": {"expression": "http://example.com"}},
            },
        }
        components = cicerone_spec.Components.from_spec(raw)
        str_repr = str(components)
        assert "<Components:" in str_repr
        assert "1 headers" in str_repr or "1 links" in str_repr or "1 callbacks" in str_repr

    def test_components_str_with_security_schemes(self):
        """Test __str__ method includes securitySchemes."""
        raw = {
            "openapi": "3.0.0",
            "components": {
                "securitySchemes": {
                    "ApiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                },
            },
        }
        components = cicerone_spec.Components.from_spec(raw)
        str_repr = str(components)
        assert "<Components:" in str_repr
        assert "1 securitySchemes" in str_repr
