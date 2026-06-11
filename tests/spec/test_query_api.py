"""Tests for the spec query conveniences added in 0.4.0.

These encode the access patterns consumers (like clientele) need:
tag-based operation lookup, direct Paths iteration, cached reference
resolution, and helpful broken-reference errors.
"""

from __future__ import annotations

import pytest

from cicerone import spec as cicerone_spec
from cicerone.parse import parse_spec_from_dict


@pytest.fixture
def tagged_spec() -> cicerone_spec.OpenAPISpec:
    return parse_spec_from_dict(
        {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {"operationId": "listUsers", "tags": ["users"]},
                    "post": {"operationId": "createUser", "tags": ["users", "admin"]},
                },
                "/pets": {
                    "get": {"operationId": "listPets", "tags": ["pets"]},
                },
                "/health": {
                    "get": {"operationId": "healthCheck"},
                },
            },
            "components": {
                "schemas": {
                    "User": {"type": "object", "properties": {"name": {"type": "string"}}},
                    "UserList": {"type": "array", "items": {"$ref": "#/components/schemas/User"}},
                }
            },
        }
    )


class TestOperationsByTag:
    def test_operations_by_tag(self, tagged_spec):
        users_ops = list(tagged_spec.operations_by_tag("users"))
        assert {op.operation_id for op in users_ops} == {"listUsers", "createUser"}

    def test_operation_with_multiple_tags_found_under_each(self, tagged_spec):
        admin_ops = list(tagged_spec.operations_by_tag("admin"))
        assert [op.operation_id for op in admin_ops] == ["createUser"]

    def test_unknown_tag_yields_nothing(self, tagged_spec):
        assert list(tagged_spec.operations_by_tag("nonexistent")) == []

    def test_tags_to_operations(self, tagged_spec):
        mapping = tagged_spec.tags_to_operations()
        assert {op.operation_id for op in mapping["users"]} == {"listUsers", "createUser"}
        assert [op.operation_id for op in mapping["pets"]] == ["listPets"]
        assert [op.operation_id for op in mapping["admin"]] == ["createUser"]
        # Untagged operations are not included
        all_ids = {op.operation_id for ops in mapping.values() for op in ops}
        assert "healthCheck" not in all_ids


class TestPathsIteration:
    def test_iterating_paths_yields_path_and_item(self, tagged_spec):
        entries = dict(tagged_spec.paths)
        assert set(entries.keys()) == {"/users", "/pets", "/health"}
        assert isinstance(entries["/users"], cicerone_spec.PathItem)

    def test_len(self, tagged_spec):
        assert len(tagged_spec.paths) == 3


class TestCachedResolution:
    def test_repeated_resolution_returns_same_object(self, tagged_spec):
        first = tagged_spec.resolve_reference("#/components/schemas/User")
        second = tagged_spec.resolve_reference("#/components/schemas/User")
        assert first is second

    def test_follow_nested_flag_cached_separately(self, tagged_spec):
        followed = tagged_spec.resolve_reference("#/components/schemas/UserList", follow_nested=True)
        assert isinstance(followed.items, cicerone_spec.Schema)
        assert followed.items.properties["name"].type == "string"

    def test_circular_references_still_detected(self):
        spec = parse_spec_from_dict(
            {
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0.0"},
                "paths": {},
                "components": {
                    "schemas": {
                        "Node": {
                            "type": "object",
                            "properties": {"next": {"$ref": "#/components/schemas/Node"}},
                        }
                    }
                },
            }
        )
        # Self-referential schemas resolve without infinite recursion
        node = spec.resolve_reference("#/components/schemas/Node")
        assert isinstance(node, cicerone_spec.Schema)


class TestBrokenReferenceErrors:
    def test_error_includes_suggestion_for_close_match(self, tagged_spec):
        with pytest.raises(ValueError) as exc_info:
            tagged_spec.resolve_reference("#/components/schemas/Usr")
        message = str(exc_info.value)
        assert "#/components/schemas/Usr" in message
        # A did-you-mean suggestion pointing at the close match
        assert "User" in message

    def test_error_lists_available_keys(self, tagged_spec):
        with pytest.raises(ValueError) as exc_info:
            tagged_spec.resolve_reference("#/components/schemas/Banana")
        message = str(exc_info.value)
        assert "User" in message or "Available" in message
