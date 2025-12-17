"""Tests for PathItem model."""

from cicerone.spec.path_item import PathItem


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
