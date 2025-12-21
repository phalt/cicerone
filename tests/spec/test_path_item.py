"""Tests for PathItem model."""

from __future__ import annotations

from cicerone import spec as cicerone_spec


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
        path_item = cicerone_spec.PathItem.from_dict("/users", data)
        assert path_item.path == "/users"
        assert "get" in path_item.operations
        assert "post" in path_item.operations
        assert path_item.operations["get"].operation_id == "getUser"
        assert path_item.operations["post"].operation_id == "createUser"

    def test_path_item_str_representation(self):
        """Test __str__ method of PathItem."""
        data = {
            "get": {"operationId": "getUser"},
            "post": {"operationId": "createUser"},
            "delete": {"operationId": "deleteUser"},
        }
        path_item = cicerone_spec.PathItem.from_dict("/users/{id}", data)
        str_repr = str(path_item)
        assert "<PathItem:" in str_repr
        assert "/users/{id}" in str_repr
        assert "GET" in str_repr
        assert "POST" in str_repr
        assert "DELETE" in str_repr

    def test_path_level_parameters_merged_into_operations(self):
        """Test that path-level parameters are merged into all operations."""
        data = {
            "parameters": [
                {"name": "request-id", "in": "header", "schema": {"type": "string"}},
                {"$ref": "#/components/parameters/api-version"},
            ],
            "get": {
                "operationId": "getUser",
                "parameters": [{"name": "x-customer-ip", "in": "header", "schema": {"type": "string"}}],
            },
            "post": {
                "operationId": "updateUser",
            },
        }
        path_item = cicerone_spec.PathItem.from_dict("/users/{id}", data)

        # GET operation should have both path-level and operation-level parameters
        get_params = path_item.operations["get"].parameters
        assert len(get_params) == 3
        # Path-level parameters should come first
        assert get_params[0]["name"] == "request-id"
        assert get_params[1]["$ref"] == "#/components/parameters/api-version"
        # Operation-level parameters should come after
        assert get_params[2]["name"] == "x-customer-ip"

        # POST operation should have only path-level parameters
        post_params = path_item.operations["post"].parameters
        assert len(post_params) == 2
        assert post_params[0]["name"] == "request-id"
        assert post_params[1]["$ref"] == "#/components/parameters/api-version"

    def test_path_level_parameters_with_no_operations_parameters(self):
        """Test path-level parameters when operations don't define their own."""
        data = {
            "parameters": [{"name": "api-key", "in": "header", "schema": {"type": "string"}}],
            "get": {"operationId": "listItems"},
            "post": {"operationId": "createItem"},
        }
        path_item = cicerone_spec.PathItem.from_dict("/items", data)

        # Both operations should have the path-level parameter
        assert len(path_item.operations["get"].parameters) == 1
        assert path_item.operations["get"].parameters[0]["name"] == "api-key"
        assert len(path_item.operations["post"].parameters) == 1
        assert path_item.operations["post"].parameters[0]["name"] == "api-key"

    def test_operations_without_path_level_parameters(self):
        """Test that operations without path-level parameters work normally."""
        data = {
            "get": {
                "operationId": "getUser",
                "parameters": [{"name": "user-id", "in": "path", "schema": {"type": "string"}}],
            },
        }
        path_item = cicerone_spec.PathItem.from_dict("/users/{id}", data)

        # Operation should only have its own parameter
        assert len(path_item.operations["get"].parameters) == 1
        assert path_item.operations["get"].parameters[0]["name"] == "user-id"
