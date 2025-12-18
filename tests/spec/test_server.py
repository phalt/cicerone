"""Tests for Server model."""

from cicerone.spec import Server, ServerVariable


class TestServerVariable:
    """Tests for ServerVariable model."""

    def test_server_variable_from_dict(self):
        """Test creating ServerVariable from dict."""
        data = {
            "default": "https",
            "enum": ["https", "http"],
            "description": "The protocol to use",
        }
        var = ServerVariable.from_dict(data)
        assert var.default == "https"
        assert var.enum == ["https", "http"]
        assert var.description == "The protocol to use"

    def test_server_variable_minimal(self):
        """Test creating ServerVariable with only required fields."""
        data = {"default": "v1"}
        var = ServerVariable.from_dict(data)
        assert var.default == "v1"
        assert var.enum == []
        assert var.description is None


class TestServer:
    """Tests for Server model."""

    def test_server_minimal(self):
        """Test creating minimal Server."""
        data = {"url": "https://api.example.com"}
        server = Server.from_dict(data)
        assert server.url == "https://api.example.com"
        assert server.description is None
        assert len(server.variables) == 0

    def test_server_with_description(self):
        """Test creating Server with description."""
        data = {
            "url": "https://api.example.com",
            "description": "Production server",
        }
        server = Server.from_dict(data)
        assert server.url == "https://api.example.com"
        assert server.description == "Production server"

    def test_server_with_variables(self):
        """Test creating Server with variables."""
        data = {
            "url": "https://{environment}.example.com",
            "variables": {
                "environment": {
                    "default": "api",
                    "enum": ["api", "staging", "dev"],
                }
            },
        }
        server = Server.from_dict(data)
        assert server.url == "https://{environment}.example.com"
        assert "environment" in server.variables
        assert server.variables["environment"].default == "api"
        assert server.variables["environment"].enum == ["api", "staging", "dev"]

    def test_server_str_representation(self):
        """Test __str__ method of Server."""
        data = {"url": "https://api.example.com"}
        server = Server.from_dict(data)
        str_repr = str(server)
        assert "<Server:" in str_repr
        assert "url=https://api.example.com" in str_repr

    def test_server_str_with_description(self):
        """Test __str__ method with description."""
        data = {
            "url": "https://api.example.com",
            "description": "Production server",
        }
        server = Server.from_dict(data)
        str_repr = str(server)
        assert "Production server" in str_repr

    def test_server_str_with_variables(self):
        """Test __str__ method with variables."""
        data = {
            "url": "https://{env}.example.com",
            "variables": {
                "env": {"default": "api"},
            },
        }
        server = Server.from_dict(data)
        str_repr = str(server)
        assert "1 variables" in str_repr
