"""Tests for Paths container."""

from cicerone.spec.paths import Paths


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
