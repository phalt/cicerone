"""Tests for Operation model."""

from cicerone.spec.operation import Operation


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
