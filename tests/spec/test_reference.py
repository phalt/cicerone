"""Tests for the Reference model and reference resolution."""

import pytest

from cicerone.parse import parse_spec_from_dict, parse_spec_from_file
from cicerone.references import Reference, ReferenceResolver


class TestReference:
    """Test the Reference model."""

    def test_basic_reference(self):
        """Test creating a basic reference."""
        ref = Reference(ref="#/components/schemas/User")
        assert ref.ref == "#/components/schemas/User"
        assert ref.summary is None
        assert ref.description is None

    def test_reference_with_summary_and_description(self):
        """Test reference with OAS 3.1 summary and description."""
        ref = Reference(
            ref="#/components/schemas/User",
            summary="User schema",
            description="Detailed user information",
        )
        assert ref.ref == "#/components/schemas/User"
        assert ref.summary == "User schema"
        assert ref.description == "Detailed user information"

    def test_reference_from_dict(self):
        """Test creating a reference from a dictionary."""
        data = {
            "$ref": "#/components/schemas/Pet",
            "summary": "Pet reference",
        }
        ref = Reference.from_dict(data)
        assert ref.ref == "#/components/schemas/Pet"
        assert ref.summary == "Pet reference"

    def test_reference_from_dict_missing_ref(self):
        """Test that from_dict raises error when $ref is missing."""
        data = {"summary": "Pet reference"}
        with pytest.raises(ValueError, match="must contain a '\\$ref' key"):
            Reference.from_dict(data)

    def test_is_local_reference(self):
        """Test detecting local references."""
        local_ref = Reference(ref="#/components/schemas/User")
        assert local_ref.is_local is True
        assert local_ref.is_external is False

    def test_is_external_reference(self):
        """Test detecting external references."""
        external_ref = Reference(ref="./models/user.yaml")
        assert external_ref.is_external is True
        assert external_ref.is_local is False

        url_ref = Reference(ref="https://example.com/schemas/user.json")
        assert url_ref.is_external is True
        assert url_ref.is_local is False

    def test_pointer_property(self):
        """Test extracting the JSON Pointer from a reference."""
        ref = Reference(ref="#/components/schemas/User")
        assert ref.pointer == "/components/schemas/User"

        ref_with_fragment = Reference(ref="./models.yaml#/Pet")
        assert ref_with_fragment.pointer == "/Pet"

        ref_no_fragment = Reference(ref="./models.yaml")
        assert ref_no_fragment.pointer == ""

    def test_document_property(self):
        """Test extracting the document part from external references."""
        local_ref = Reference(ref="#/components/schemas/User")
        assert local_ref.document == ""

        file_ref = Reference(ref="./models.yaml#/Pet")
        assert file_ref.document == "./models.yaml"

        file_ref_no_fragment = Reference(ref="./models.yaml")
        assert file_ref_no_fragment.document == "./models.yaml"

    def test_pointer_parts(self):
        """Test splitting the pointer into parts."""
        ref = Reference(ref="#/components/schemas/User")
        assert ref.pointer_parts == ["components", "schemas", "User"]

        ref_root = Reference(ref="#/")
        assert ref_root.pointer_parts == []

        ref_no_pointer = Reference(ref="./models.yaml")
        assert ref_no_pointer.pointer_parts == []

    def test_is_reference_static_method(self):
        """Test the is_reference static method."""
        assert Reference.is_reference({"$ref": "#/components/schemas/User"}) is True
        assert Reference.is_reference({"type": "object"}) is False
        assert Reference.is_reference("not a dict") is False
        assert Reference.is_reference(None) is False

    def test_reference_str_representation(self):
        """Test string representation of references."""
        ref = Reference(ref="#/components/schemas/User")
        str_repr = str(ref)
        assert "Reference" in str_repr
        assert "#/components/schemas/User" in str_repr

    def test_reference_str_with_summary(self):
        """Test string representation with summary."""
        ref = Reference(
            ref="#/components/schemas/User",
            summary="A very long summary that should be truncated when displayed in the string representation",
        )
        str_repr = str(ref)
        assert "summary=" in str_repr
        assert "..." in str_repr

    def test_reference_str_with_description(self):
        """Test string representation with description."""
        ref = Reference(
            ref="#/components/schemas/User",
            description="A very long description that should be truncated when displayed",
        )
        str_repr = str(ref)
        assert "description=" in str_repr
        assert "..." in str_repr


class TestReferenceResolver:
    """Test the ReferenceResolver class."""

    def test_resolve_simple_local_reference(self):
        """Test resolving a simple local reference to a schema."""
        from cicerone.spec import Schema

        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")
        resolver = ReferenceResolver(spec)

        user_schema = resolver.resolve_reference("#/components/schemas/User")
        assert isinstance(user_schema, Schema)
        assert user_schema.type == "object"
        assert "id" in user_schema.properties
        assert "username" in user_schema.properties

    def test_resolve_reference_with_reference_object(self):
        """Test resolving using a Reference object."""
        from cicerone.spec import Schema

        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")
        resolver = ReferenceResolver(spec)

        ref = Reference(ref="#/components/schemas/User")
        user_schema = resolver.resolve_reference(ref)
        assert isinstance(user_schema, Schema)
        assert user_schema.type == "object"

    def test_resolve_reference_not_found(self):
        """Test resolving a reference that doesn't exist."""
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")
        resolver = ReferenceResolver(spec)

        with pytest.raises(ValueError, match="Reference path not found"):
            resolver.resolve_reference("#/components/schemas/NonExistent")

    def test_resolve_reference_invalid_path(self):
        """Test resolving a reference with an invalid path."""
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")
        resolver = ReferenceResolver(spec)

        with pytest.raises(ValueError, match="Reference path not found"):
            resolver.resolve_reference("#/components/invalid/path")

    def test_resolve_nested_reference(self):
        """Test resolving nested references."""
        from cicerone.spec import Schema

        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "User": {"$ref": "#/components/schemas/Person"},
                    "Person": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # With follow_nested=True (default), should resolve to Person
        person_schema = resolver.resolve_reference("#/components/schemas/User")
        assert isinstance(person_schema, Schema)
        assert person_schema.type == "object"
        assert "name" in person_schema.properties

        # With follow_nested=False, should return the reference dict
        user_ref = resolver.resolve_reference("#/components/schemas/User", follow_nested=False)
        assert "$ref" in user_ref

    def test_resolve_deeply_nested_references(self):
        """Test resolving deeply nested references in schema properties."""
        from cicerone.spec import Schema

        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                        },
                    },
                    "User": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "address": {"$ref": "#/components/schemas/Address"},
                        },
                    },
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # With follow_nested=True, nested $refs in properties should be resolved
        user_schema = resolver.resolve_reference("#/components/schemas/User", follow_nested=True)
        assert isinstance(user_schema, Schema)
        assert user_schema.type == "object"

        # The address property should now be a fully resolved Schema, not a ref
        address_prop = user_schema.properties["address"]
        assert isinstance(address_prop, Schema)
        assert address_prop.type == "object"
        assert "street" in address_prop.properties
        assert "city" in address_prop.properties

        # Verify the nested properties are also Schema objects
        street_prop = address_prop.properties["street"]
        assert isinstance(street_prop, Schema)
        assert street_prop.type == "string"

    def test_circular_reference_detection(self):
        """Test detecting circular references."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "A": {"$ref": "#/components/schemas/B"},
                    "B": {"$ref": "#/components/schemas/C"},
                    "C": {"$ref": "#/components/schemas/A"},
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # Trying to fully resolve A should detect the circular chain
        with pytest.raises(RecursionError, match="Circular reference detected"):
            resolver.resolve_reference("#/components/schemas/A", follow_nested=True)

    def test_get_all_references(self):
        """Test finding all references in a spec."""
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")
        resolver = ReferenceResolver(spec)

        all_refs = resolver.get_all_references()
        assert isinstance(all_refs, dict)
        assert len(all_refs) > 0
        assert all(isinstance(v, Reference) for v in all_refs.values())
        assert all(isinstance(k, str) for k in all_refs.keys())

        # Check that we found the User schema references
        user_refs = {k: v for k, v in all_refs.items() if "User" in k}
        assert len(user_refs) > 0

    def test_get_all_references_empty_spec(self):
        """Test finding references in a spec without any."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        all_refs = resolver.get_all_references()
        assert isinstance(all_refs, dict)
        assert len(all_refs) == 0

    def test_is_circular_reference(self):
        """Test checking if a reference is circular."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Node": {
                        "type": "object",
                        "properties": {
                            "children": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/Node"},
                            }
                        },
                    },
                    "User": {"type": "object", "properties": {"name": {"type": "string"}}},
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # User is not circular
        assert resolver.is_circular_reference("#/components/schemas/User") is False

        # Node contains a circular reference in its items
        # Note: We can resolve the schema itself, but the nested ref is circular
        assert resolver.is_circular_reference("#/components/schemas/Node") is False

    def test_external_reference_not_supported(self):
        """Test that external references raise an appropriate error."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "User": {"$ref": "./models/user.yaml#/User"},
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        with pytest.raises(ValueError, match="External references are not yet supported"):
            resolver.resolve_reference("./models/user.yaml#/User")

    def test_resolve_root_reference(self):
        """Test resolving a reference to the root document."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        root = resolver.resolve_reference("#")
        assert isinstance(root, dict)
        assert root == spec_data

    def test_resolve_reference_with_array_index(self):
        """Test resolving a reference with array indexing."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "tags": [
                {"name": "users", "description": "User operations"},
                {"name": "posts", "description": "Post operations"},
            ],
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        tag = resolver.resolve_reference("#/tags/1")
        assert isinstance(tag, dict)
        assert tag["name"] == "posts"

    def test_resolve_reference_invalid_array_index(self):
        """Test resolving a reference with invalid array index."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "tags": [{"name": "users"}],
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # Non-numeric index
        with pytest.raises(ValueError, match="Reference path not found"):
            resolver.resolve_reference("#/tags/invalid")

        # Out of bounds index
        with pytest.raises(ValueError, match="Reference path not found"):
            resolver.resolve_reference("#/tags/10")

    def test_resolve_reference_through_non_dict_list(self):
        """Test resolving a reference through a non-dict/list object."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # Try to navigate through a string value
        with pytest.raises(ValueError, match="Cannot navigate through non-dict/list object"):
            resolver.resolve_reference("#/openapi/invalid/path")

    def test_resolve_non_local_reference_error(self):
        """Test resolving a non-local reference to _resolve_local_reference raises error."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        ref = Reference(ref="./external.yaml")
        with pytest.raises(ValueError, match="Expected local reference"):
            resolver._resolve_local_reference(ref)


class TestOpenAPISpecReferenceIntegration:
    """Test reference methods integrated into OpenAPISpec."""

    def test_resolve_reference_from_spec(self):
        """Test resolving a reference directly from the spec."""
        from cicerone.spec import Schema

        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")

        user_schema = spec.resolve_reference("#/components/schemas/User")
        assert isinstance(user_schema, Schema)
        assert user_schema.type == "object"
        assert "username" in user_schema.properties

    def test_get_all_references_from_spec(self):
        """Test getting all references directly from the spec."""
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")

        all_refs = spec.get_all_references()
        assert isinstance(all_refs, dict)
        assert len(all_refs) > 0
        assert all(isinstance(v, Reference) for v in all_refs.values())
        assert all(isinstance(k, str) for k in all_refs.keys())

        # All refs should be local in this fixture
        assert all(v.is_local for v in all_refs.values())

    def test_is_circular_reference_from_spec(self):
        """Test checking for circular references using the resolver directly."""
        from cicerone.references import ReferenceResolver

        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Node": {
                        "type": "object",
                        "properties": {
                            "children": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/Node"},
                            }
                        },
                    }
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # The schema itself is not circular, but contains a circular reference
        assert resolver.is_circular_reference("#/components/schemas/Node") is False

    def test_is_circular_reference_true(self):
        """Test detecting a truly circular reference using the resolver directly."""
        from cicerone.references import ReferenceResolver

        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "A": {"$ref": "#/components/schemas/B"},
                    "B": {"$ref": "#/components/schemas/A"},
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # This creates a true circular chain
        assert resolver.is_circular_reference("#/components/schemas/A") is True

    def test_resolve_reference_in_paths(self):
        """Test resolving references found in paths."""
        from cicerone.spec import Schema

        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")

        # Find a reference in the paths section
        all_refs = spec.get_all_references()
        path_refs = {k: v for k, v in all_refs.items() if k.endswith("/User")}

        assert len(path_refs) > 0

        # Resolve one of them
        first_ref_key = list(path_refs.keys())[0]
        resolved = spec.resolve_reference(path_refs[first_ref_key])
        assert isinstance(resolved, Schema)
        assert resolved.type == "object"

    def test_resolve_path_items_component(self):
        """Test resolving pathItems component (OpenAPI 3.1).

        Note: pathItems in components returns raw dict since PathItem requires
        a path argument which isn't available in the component context.
        """
        spec_data = {
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/users": {"$ref": "#/components/pathItems/UsersPath"}},
            "components": {
                "pathItems": {
                    "UsersPath": {
                        "get": {
                            "summary": "List users",
                            "responses": {
                                "200": {
                                    "description": "Success",
                                    "content": {"application/json": {"schema": {"type": "array"}}},
                                }
                            },
                        }
                    }
                }
            },
        }
        spec = parse_spec_from_dict(spec_data)
        resolver = ReferenceResolver(spec)

        # Resolve the pathItems reference - returns raw dict
        path_item_data = resolver.resolve_reference("#/components/pathItems/UsersPath")
        assert isinstance(path_item_data, dict)
        assert "get" in path_item_data
        assert path_item_data["get"]["summary"] == "List users"


# Additional tests to achieve 100% coverage


def test_reference_model_dump():
    """Test Reference serialization with $ref."""
    from cicerone.references import Reference

    ref = Reference(ref="#/components/schemas/User")
    dumped = ref.model_dump()
    assert "$ref" in dumped
    assert dumped["$ref"] == "#/components/schemas/User"
    assert "ref" not in dumped


def test_resolve_short_reference():
    """Test resolving a reference with < 2 parts."""
    from cicerone.parse import parse_spec_from_dict
    from cicerone.references import ReferenceResolver

    spec_data = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {},
    }
    spec = parse_spec_from_dict(spec_data)
    resolver = ReferenceResolver(spec)

    # Reference with single part should return raw data
    result = resolver.resolve_reference("#")
    assert result == spec.raw


def test_resolve_non_pydantic_object():
    """Test _resolve_nested_references with non-Pydantic object."""
    from cicerone.parse import parse_spec_from_dict
    from cicerone.references import ReferenceResolver

    spec_data = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {},
    }
    spec = parse_spec_from_dict(spec_data)
    resolver = ReferenceResolver(spec)

    # Should return the same object if not a Pydantic model
    result = resolver._resolve_nested_references("string")
    assert result == "string"

    result = resolver._resolve_nested_references(123)
    assert result == 123


def test_resolve_root_reference():
    """Test resolving root # reference."""
    from cicerone.parse import parse_spec_from_dict
    from cicerone.references import ReferenceResolver

    spec_data = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {},
    }
    spec = parse_spec_from_dict(spec_data)
    resolver = ReferenceResolver(spec)

    # Root reference should return the entire spec dict
    result = resolver.resolve_reference("#")
    assert result == spec.raw


def test_circular_reference_creates_linked_structure():
    """Test that circular references create appropriate linked structures."""
    from cicerone.parse import parse_spec_from_dict
    from cicerone.references import ReferenceResolver
    from cicerone.spec import Schema

    spec_data = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {},
        "components": {
            "schemas": {
                "Node": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "next": {"$ref": "#/components/schemas/Node"},
                    },
                }
            }
        },
    }
    spec = parse_spec_from_dict(spec_data)
    resolver = ReferenceResolver(spec)

    # Resolve with follow_nested=True should handle circular reference
    node = resolver.resolve_reference("#/components/schemas/Node", follow_nested=True)
    assert isinstance(node, Schema)
    # The circular reference should be detected and handled
    assert isinstance(node.properties["next"], Schema)


def test_resolve_path_item_with_proper_format():
    """Test resolving a path directly (not via reference)."""
    from cicerone.parse import parse_spec_from_dict
    from cicerone.references import Reference, ReferenceResolver

    spec_data = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "List users",
                    "responses": {"200": {"description": "Success"}},
                }
            }
        },
    }
    spec = parse_spec_from_dict(spec_data)
    resolver = ReferenceResolver(spec)

    # Test the _convert_to_typed_object method directly with paths
    ref = Reference(ref="#/paths/users")
    data = {"get": {"summary": "List users", "responses": {"200": {"description": "Success"}}}}
    result = resolver._convert_to_typed_object(ref, data)
    # This should trigger the paths handling code path
    assert result is not None


def test_resolve_single_part_reference():
    """Test resolving a reference with single part returns raw data."""
    from cicerone.parse import parse_spec_from_dict
    from cicerone.references import Reference, ReferenceResolver

    spec_data = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {},
    }
    spec = parse_spec_from_dict(spec_data)
    resolver = ReferenceResolver(spec)

    # Test with a reference that has only one part after #
    ref = Reference(ref="#/openapi")
    data = "3.0.0"
    # This should return the raw data since parts < 2 after splitting
    result = resolver._convert_to_typed_object(ref, data)
    assert result == "3.0.0"
