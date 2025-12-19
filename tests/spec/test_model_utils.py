"""Tests for model_utils parsing utilities."""

from __future__ import annotations

from cicerone.spec import model_utils


def dummy_parser(data: dict) -> dict:
    """Simple parser for testing that adds a 'parsed' flag."""
    return {**data, "parsed": True}


class TestParseNestedObject:
    """Tests for parse_nested_object function."""

    def test_parse_nested_object_when_field_exists(self):
        """Test parsing a nested object when the field exists."""
        data = {
            "name": "test",
            "nested": {"key": "value"},
        }
        result = model_utils.parse_nested_object(data, "nested", dummy_parser)
        assert result == {"key": "value", "parsed": True}

    def test_parse_nested_object_when_field_missing(self):
        """Test parsing a nested object when the field is missing."""
        data = {"name": "test"}
        result = model_utils.parse_nested_object(data, "nested", dummy_parser)
        assert result is None

    def test_parse_nested_object_with_empty_dict(self):
        """Test parsing with an empty dictionary."""
        data: dict[str, str] = {}
        result = model_utils.parse_nested_object(data, "nested", dummy_parser)
        assert result is None

    def test_parse_nested_object_preserves_parser_behavior(self):
        """Test that the parser function is called correctly."""
        data = {"nested": {"a": 1, "b": 2}}

        def custom_parser(d: dict) -> dict:
            return {"sum": sum(d.values())}

        result = model_utils.parse_nested_object(data, "nested", custom_parser)
        assert result == {"sum": 3}


class TestParseCollection:
    """Tests for parse_collection function."""

    def test_parse_collection_when_field_exists(self):
        """Test parsing a collection when the field exists."""
        data = {
            "items": {
                "item1": {"value": 1},
                "item2": {"value": 2},
            }
        }
        result = model_utils.parse_collection(data, "items", dummy_parser)
        assert result == {
            "item1": {"value": 1, "parsed": True},
            "item2": {"value": 2, "parsed": True},
        }

    def test_parse_collection_when_field_missing(self):
        """Test parsing a collection when the field is missing."""
        data = {"other": "value"}
        result = model_utils.parse_collection(data, "items", dummy_parser)
        assert result == {}

    def test_parse_collection_with_empty_collection(self):
        """Test parsing an empty collection."""
        data: dict[str, dict[str, dict[str, str]]] = {"items": {}}
        result = model_utils.parse_collection(data, "items", dummy_parser)
        assert result == {}

    def test_parse_collection_with_multiple_items(self):
        """Test parsing a collection with multiple items."""
        data = {
            "examples": {
                "ex1": {"name": "first"},
                "ex2": {"name": "second"},
                "ex3": {"name": "third"},
            }
        }

        def name_parser(d: dict) -> dict:
            return {"parsed_name": d["name"].upper()}

        result = model_utils.parse_collection(data, "examples", name_parser)
        assert len(result) == 3
        assert result["ex1"] == {"parsed_name": "FIRST"}
        assert result["ex2"] == {"parsed_name": "SECOND"}
        assert result["ex3"] == {"parsed_name": "THIRD"}

    def test_parse_collection_preserves_key_names(self):
        """Test that collection parsing preserves the original key names."""
        data = {
            "schemas": {
                "User": {"type": "object"},
                "Address": {"type": "object"},
            }
        }
        result = model_utils.parse_collection(data, "schemas", dummy_parser)
        assert "User" in result
        assert "Address" in result
        assert result["User"]["parsed"] is True
        assert result["Address"]["parsed"] is True
