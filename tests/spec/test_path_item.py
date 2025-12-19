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
