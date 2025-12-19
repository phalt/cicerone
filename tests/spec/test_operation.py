"""Tests for Operation model."""

from __future__ import annotations

from cicerone import spec as cicerone_spec


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
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        assert operation.method == "GET"
        assert operation.path == "/users"
        assert operation.operation_id == "listUsers"
        assert operation.summary == "List users"
        assert operation.description == "Get all users"
        assert operation.tags == ["users"]
        assert len(operation.parameters) == 1
        assert "200" in operation.responses

    def test_operation_str_representation(self):
        """Test __str__ method of Operation."""
        data = {
            "operationId": "listUsers",
            "summary": "List users",
            "tags": ["users"],
        }
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        str_repr = str(operation)
        assert "<Operation:" in str_repr
        assert "GET /users" in str_repr
        assert "id=listUsers" in str_repr
        assert "'List users'" in str_repr
        assert "tags=['users']" in str_repr

    def test_operation_str_without_optional_fields(self):
        """Test __str__ method without optional fields."""
        data: dict[str, str] = {}
        operation = cicerone_spec.Operation.from_dict("POST", "/posts", data)
        str_repr = str(operation)
        assert "<Operation:" in str_repr
        assert "POST /posts" in str_repr
        # Should not include operationId, summary, or tags if not present
        assert "id=" not in str_repr or "id=None" not in str_repr
