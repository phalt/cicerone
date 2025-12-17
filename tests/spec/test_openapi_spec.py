"""Tests for OpenAPISpec model."""

import json
from pathlib import Path

from cicerone.parse import parse_spec_from_dict, parse_spec_from_file, parse_spec_from_json, parse_spec_from_yaml


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

        spec = parse_spec_from_dict(data)

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
        fixture_path = Path(__file__).parent.parent / "fixtures" / "petstore_openapi3.yaml"
        spec = parse_spec_from_file(fixture_path)

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
        fixture_path = Path(__file__).parent.parent / "fixtures" / "swagger2.yaml"
        spec = parse_spec_from_file(fixture_path)

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
        spec = parse_spec_from_json(json_str)
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
        spec = parse_spec_from_yaml(yaml_str)
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
        spec = parse_spec_from_dict(data)

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
        spec = parse_spec_from_dict(data)

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
        spec = parse_spec_from_dict(data)
        assert spec.raw["openapi"] == "3.0.0"
        assert spec.raw["info"]["title"] == "Test API"
