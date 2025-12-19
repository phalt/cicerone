"""Tests for Paths container."""

from __future__ import annotations

import typing

from cicerone import spec as cicerone_spec


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
        paths = cicerone_spec.Paths.from_dict(data)
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
        paths = cicerone_spec.Paths.from_dict(data)
        operations = list(paths.all_operations())
        assert len(operations) == 3
        op_ids = [op.operation_id for op in operations]
        assert "listUsers" in op_ids
        assert "createUser" in op_ids
        assert "listPosts" in op_ids

    def test_paths_str_representation(self):
        """Test __str__ method of Paths."""
        data = {
            "/users": {
                "get": {"operationId": "listUsers"},
                "post": {"operationId": "createUser"},
            },
            "/posts": {
                "get": {"operationId": "listPosts"},
            },
        }
        paths = cicerone_spec.Paths.from_dict(data)
        str_repr = str(paths)
        assert "<Paths:" in str_repr
        assert "2 paths" in str_repr
        assert "3 operations" in str_repr
        assert "/users" in str_repr
        assert "/posts" in str_repr

    def test_paths_str_many_paths(self):
        """Test __str__ method with many paths (should truncate)."""
        data: dict[str, typing.Any] = {f"/path{i}": {"get": {}} for i in range(10)}
        paths = cicerone_spec.Paths.from_dict(data)
        str_repr = str(paths)
        assert "10 paths" in str_repr
        assert "(+7 more)" in str_repr
