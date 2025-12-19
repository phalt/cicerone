"""Tests for component models."""

from __future__ import annotations

from cicerone import spec as cicerone_spec


class TestParameter:
    """Tests for Parameter model."""

    def test_parameter_from_dict(self):
        """Test creating Parameter from dict."""
        data = {
            "name": "page",
            "in": "query",
            "description": "Page number",
            "required": False,
            "schema": {"type": "integer"},
        }
        param = cicerone_spec.Parameter.from_dict(data)
        assert param.name == "page"
        assert param.in_ == "query"
        assert param.description == "Page number"
        assert param.required is False
        assert param.schema_ is not None
        assert param.schema_.type == "integer"


class TestResponse:
    """Tests for Response model."""

    def test_response_from_dict(self):
        """Test creating Response from dict."""
        data = {
            "description": "Success response",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
        }
        response = cicerone_spec.Response.from_dict(data)
        assert response.description == "Success response"
        assert "application/json" in response.content


class TestRequestBody:
    """Tests for RequestBody model."""

    def test_request_body_from_dict(self):
        """Test creating RequestBody from dict."""
        data = {
            "description": "User request body",
            "required": True,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
        }
        body = cicerone_spec.RequestBody.from_dict(data)
        assert body.description == "User request body"
        assert body.required is True
        assert "application/json" in body.content


class TestSecurityScheme:
    """Tests for SecurityScheme model."""

    def test_security_scheme_http(self):
        """Test creating HTTP SecurityScheme from dict."""
        data = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Bearer token authentication",
        }
        scheme = cicerone_spec.SecurityScheme.from_dict(data)
        assert scheme.type == "http"
        assert scheme.scheme == "bearer"
        assert scheme.bearerFormat == "JWT"

    def test_security_scheme_apikey(self):
        """Test creating API key SecurityScheme from dict."""
        data = {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
        }
        scheme = cicerone_spec.SecurityScheme.from_dict(data)
        assert scheme.type == "apiKey"
        assert scheme.name == "X-API-Key"
        assert scheme.in_ == "header"


class TestExample:
    """Tests for Example model."""

    def test_example_from_dict(self):
        """Test creating Example from dict."""
        data = {
            "summary": "Example user",
            "value": {"id": "123", "name": "John"},
        }
        example = cicerone_spec.Example.from_dict(data)
        assert example.summary == "Example user"
        assert example.value == {"id": "123", "name": "John"}


class TestHeader:
    """Tests for Header model."""

    def test_header_from_dict(self):
        """Test creating Header from dict."""
        data = {
            "description": "Rate limit header",
            "schema": {"type": "integer"},
        }
        header = cicerone_spec.Header.from_dict(data)
        assert header.description == "Rate limit header"
        assert header.schema_ is not None
        assert header.schema_.type == "integer"
