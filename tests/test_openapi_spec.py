"""Tests for OpenAPI specification models and parsing."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

from cicerone.spec import Components, OpenAPISpec, Operation, PathItem, Paths, Schema, Version


class TestVersion:
    """Tests for Version class."""

    def test_version_parsing_openapi3(self):
        """Test parsing OpenAPI 3.x version strings."""
        version = Version("3.0.0")
        assert version.major == 3
        assert version.minor == 0
        assert version.patch == 0
        assert version.raw == "3.0.0"
        assert str(version) == "3.0.0"

    def test_version_parsing_openapi31(self):
        """Test parsing OpenAPI 3.1.x version strings."""
        version = Version("3.1.0")
        assert version.major == 3
        assert version.minor == 1
        assert version.patch == 0

    def test_version_parsing_swagger2(self):
        """Test parsing Swagger 2.0 version strings."""
        version = Version("2.0")
        assert version.major == 2
        assert version.minor == 0
        assert version.patch == 0


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


class TestOperation:
    """Tests for Operation model."""

    def test_basic_operation(self):
        """Test creating a basic operation."""
        data = {
            "operationId": "listUsers",
            "summary": "List users",
            "description": "Get all users",
            "tags": ["users"],
            "parameters": [{"name": "limit", "in": "query"}],
            "responses": {"200": {"description": "OK"}},
        }
        operation = Operation.from_dict("GET", "/users", data)
        assert operation.method == "GET"
        assert operation.path == "/users"
        assert operation.operation_id == "listUsers"
        assert operation.summary == "List users"
        assert operation.description == "Get all users"
        assert operation.tags == ["users"]
        assert len(operation.parameters) == 1
        assert "200" in operation.responses


class TestPathItem:
    """Tests for PathItem model."""

    def test_path_item_with_operations(self):
        """Test creating a path item with multiple operations."""
        data = {
            "get": {
                "operationId": "getUser",
                "summary": "Get user",
            },
            "post": {
                "operationId": "createUser",
                "summary": "Create user",
            },
        }
        path_item = PathItem.from_dict("/users", data)
        assert path_item.path == "/users"
        assert "get" in path_item.operations
        assert "post" in path_item.operations
        assert path_item.operations["get"].operation_id == "getUser"
        assert path_item.operations["post"].operation_id == "createUser"


class TestPaths:
    """Tests for Paths container."""

    def test_paths_from_dict(self):
        """Test creating Paths from dictionary."""
        data = {
            "/users": {
                "get": {"operationId": "listUsers"},
            },
            "/posts": {
                "get": {"operationId": "listPosts"},
            },
        }
        paths = Paths.from_dict(data)
        assert "/users" in paths
        assert "/posts" in paths
        assert paths["/users"].path == "/users"

    def test_all_operations(self):
        """Test getting all operations across paths."""
        data = {
            "/users": {
                "get": {"operationId": "listUsers"},
                "post": {"operationId": "createUser"},
            },
            "/posts": {
                "get": {"operationId": "listPosts"},
            },
        }
        paths = Paths.from_dict(data)
        operations = list(paths.all_operations())
        assert len(operations) == 3
        op_ids = [op.operation_id for op in operations]
        assert "listUsers" in op_ids
        assert "createUser" in op_ids
        assert "listPosts" in op_ids


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
        user_schema = components.get("User")
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
        assert components.get("Pet") is not None


class TestOpenAPISpec:
    """Tests for OpenAPISpec top-level model."""

    def test_minimal_openapi3_embedded(self):
        """Test parsing a minimal embedded OpenAPI 3.0 spec."""
        data = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List users",
                        "tags": ["users"],
                    },
                },
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["id", "username"],
                        "properties": {
                            "id": {"type": "string"},
                            "username": {"type": "string"},
                        },
                    },
                },
            },
        }

        spec = OpenAPISpec.from_dict(data)

        # Verify version
        assert spec.version.major == 3
        assert spec.version.minor == 0
        assert spec.version.patch == 0

        # Verify paths
        assert "/users" in spec.paths
        assert "get" in spec.paths["/users"].operations
        assert spec.paths["/users"].operations["get"].operation_id == "listUsers"

        # Verify components
        user_schema = spec.components.get("User")
        assert user_schema is not None
        assert user_schema.type == "object"
        assert user_schema.required == ["id", "username"]
        assert "id" in user_schema.properties
        assert "username" in user_schema.properties

    def test_openapi3_from_file(self):
        """Test loading OpenAPI 3.0 spec from file."""
        fixture_path = Path(__file__).parent / "fixtures" / "petstore_openapi3.yaml"
        spec = OpenAPISpec.from_file(fixture_path)

        # Verify basic structure
        assert spec.version.major == 3

        # Verify paths exist
        assert len(spec.paths.items) > 0
        assert "/users" in spec.paths

        # Verify operations
        list_users_op = spec.operation_by_operation_id("listUsers")
        assert list_users_op is not None
        assert list_users_op.method == "GET"
        assert list_users_op.path == "/users"
        assert "users" in list_users_op.tags

        create_user_op = spec.operation_by_operation_id("createUser")
        assert create_user_op is not None
        assert create_user_op.method == "POST"

        get_user_op = spec.operation_by_operation_id("getUser")
        assert get_user_op is not None
        assert get_user_op.path == "/users/{userId}"

        # Verify schemas
        user_schema = spec.components.get("User")
        assert user_schema is not None
        assert user_schema.type == "object"
        assert "id" in user_schema.required
        assert "username" in user_schema.required
        assert "email" in user_schema.required
        assert "id" in user_schema.properties
        assert "username" in user_schema.properties
        assert "email" in user_schema.properties
        assert "age" in user_schema.properties
        assert "roles" in user_schema.properties

        error_schema = spec.components.get("Error")
        assert error_schema is not None

        # Verify all_operations
        all_ops = list(spec.all_operations())
        assert len(all_ops) >= 3

    def test_swagger2_from_file(self):
        """Test loading Swagger 2.0 spec from file."""
        fixture_path = Path(__file__).parent / "fixtures" / "swagger2.yaml"
        spec = OpenAPISpec.from_file(fixture_path)

        # Verify version
        assert spec.version.major == 2
        assert spec.version.minor == 0

        # Verify paths
        assert "/pets" in spec.paths

        # Verify operations
        list_pets_op = spec.operation_by_operation_id("listPets")
        assert list_pets_op is not None
        assert list_pets_op.method == "GET"

        create_pet_op = spec.operation_by_operation_id("createPet")
        assert create_pet_op is not None
        assert create_pet_op.method == "POST"

        # Verify schemas from definitions
        pet_schema = spec.components.get("Pet")
        assert pet_schema is not None
        assert pet_schema.type == "object"
        assert "id" in pet_schema.required
        assert "name" in pet_schema.required
        assert "id" in pet_schema.properties
        assert "name" in pet_schema.properties

    def test_from_json(self):
        """Test parsing from JSON string."""
        json_str = json.dumps(
            {
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0.0"},
                "paths": {
                    "/test": {
                        "get": {"operationId": "getTest"},
                    },
                },
            }
        )
        spec = OpenAPISpec.from_json(json_str)
        assert spec.version.major == 3
        assert "/test" in spec.paths

    def test_from_yaml(self):
        """Test parsing from YAML string."""
        yaml_str = """
openapi: "3.0.0"
info:
  title: Test
  version: "1.0.0"
paths:
  /test:
    get:
      operationId: getTest
"""
        spec = OpenAPISpec.from_yaml(yaml_str)
        assert spec.version.major == 3
        assert "/test" in spec.paths

    def test_operation_by_operation_id(self):
        """Test finding operations by operationId."""
        data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {"operationId": "listUsers"},
                    "post": {"operationId": "createUser"},
                },
                "/posts": {
                    "get": {"operationId": "listPosts"},
                },
            },
        }
        spec = OpenAPISpec.from_dict(data)

        # Find existing operation
        op = spec.operation_by_operation_id("listUsers")
        assert op is not None
        assert op.method == "GET"
        assert op.path == "/users"

        # Try to find non-existent operation
        op = spec.operation_by_operation_id("nonExistent")
        assert op is None

    def test_all_operations(self):
        """Test iterating all operations."""
        data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {"operationId": "listUsers"},
                    "post": {"operationId": "createUser"},
                },
                "/posts": {
                    "get": {"operationId": "listPosts"},
                },
            },
        }
        spec = OpenAPISpec.from_dict(data)

        operations = list(spec.all_operations())
        assert len(operations) == 3
        op_ids = [op.operation_id for op in operations]
        assert "listUsers" in op_ids
        assert "createUser" in op_ids
        assert "listPosts" in op_ids

    def test_raw_access(self):
        """Test accessing raw spec data."""
        data = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }
        spec = OpenAPISpec.from_dict(data)
        assert spec.raw["openapi"] == "3.0.0"
        assert spec.raw["info"]["title"] == "Test API"

    def test_from_url_json(self):
        """Test loading spec from URL with JSON content."""
        json_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {"operationId": "getTest"},
                },
            },
        }

        # Mock the urlopen call
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(json_spec).encode("utf-8")
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch("cicerone.spec.models.urlopen", return_value=mock_response):
            spec = OpenAPISpec.from_url("https://example.com/openapi.json")
            assert spec.version.major == 3
            assert "/test" in spec.paths

    def test_from_url_yaml(self):
        """Test loading spec from URL with YAML content."""
        yaml_spec = """
openapi: "3.0.0"
info:
  title: Test
  version: "1.0.0"
paths:
  /test:
    get:
      operationId: getTest
"""

        # Mock the urlopen call
        mock_response = Mock()
        mock_response.read.return_value = yaml_spec.encode("utf-8")
        mock_response.headers = {"Content-Type": "application/yaml"}
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch("cicerone.spec.models.urlopen", return_value=mock_response):
            spec = OpenAPISpec.from_url("https://example.com/openapi.yaml")
            assert spec.version.major == 3
            assert "/test" in spec.paths
