"""Tests for component models."""

from cicerone import spec


class TestParameter:
    """Tests for spec.parameter.Parameter model."""

    def test_parameter_from_dict(self):
        """Test creating spec.parameter.Parameter from dict."""
        data = {
            "name": "page",
            "in": "query",
            "description": "Page number",
            "required": False,
            "schema": {"type": "integer"},
        }
        param = Parameter.from_dict(data)
        assert param.name == "page"
        assert param.in_ == "query"
        assert param.description == "Page number"
        assert param.required is False
        assert param.schema_ is not None
        assert param.schema_.type == "integer"


class TestResponse:
    """Tests for spec.response.Response model."""

    def test_response_from_dict(self):
        """Test creating spec.response.Response from dict."""
        data = {
            "description": "Success response",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
        }
        response = Response.from_dict(data)
        assert response.description == "Success response"
        assert "application/json" in response.content


class TestRequestBody:
    """Tests for spec.requestbody.RequestBody model."""

    def test_request_body_from_dict(self):
        """Test creating spec.requestbody.RequestBody from dict."""
        data = {
            "description": "User request body",
            "required": True,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
        }
        body = RequestBody.from_dict(data)
        assert body.description == "User request body"
        assert body.required is True
        assert "application/json" in body.content


class TestSecurityScheme:
    """Tests for spec.securityscheme.SecurityScheme model."""

    def test_security_scheme_http(self):
        """Test creating HTTP spec.securityscheme.SecurityScheme from dict."""
        data = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Bearer token authentication",
        }
        scheme = SecurityScheme.from_dict(data)
        assert scheme.type == "http"
        assert scheme.scheme == "bearer"
        assert scheme.bearerFormat == "JWT"

    def test_security_scheme_apikey(self):
        """Test creating API key spec.securityscheme.SecurityScheme from dict."""
        data = {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
        }
        scheme = SecurityScheme.from_dict(data)
        assert scheme.type == "apiKey"
        assert scheme.name == "X-API-Key"
        assert scheme.in_ == "header"


class TestExample:
    """Tests for spec.example.Example model."""

    def test_example_from_dict(self):
        """Test creating spec.example.Example from dict."""
        data = {
            "summary": "spec.example.Example user",
            "value": {"id": "123", "name": "John"},
        }
        example = Example.from_dict(data)
        assert example.summary == "spec.example.Example user"
        assert example.value == {"id": "123", "name": "John"}


class TestHeader:
    """Tests for spec.header.Header model."""

    def test_header_from_dict(self):
        """Test creating spec.header.Header from dict."""
        data = {
            "description": "Rate limit header",
            "schema": {"type": "integer"},
        }
        header = Header.from_dict(data)
        assert header.description == "Rate limit header"
        assert header.schema_ is not None
        assert header.schema_.type == "integer"
