"""Tests for the Reference model and reference resolution."""

import pytest

from cicerone.parse import parse_spec_from_dict, parse_spec_from_file
from cicerone.spec import Reference, ReferenceResolver


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
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")
        resolver = ReferenceResolver(spec)

        user_schema = resolver.resolve_reference("#/components/schemas/User")
        assert user_schema["type"] == "object"
        assert "id" in user_schema["properties"]
        assert "username" in user_schema["properties"]

    def test_resolve_reference_with_reference_object(self):
        """Test resolving using a Reference object."""
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")
        resolver = ReferenceResolver(spec)

        ref = Reference(ref="#/components/schemas/User")
        user_schema = resolver.resolve_reference(ref)
        assert user_schema["type"] == "object"

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
        assert person_schema["type"] == "object"
        assert "name" in person_schema["properties"]

        # With follow_nested=False, should return the reference
        user_ref = resolver.resolve_reference("#/components/schemas/User", follow_nested=False)
        assert "$ref" in user_ref

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
        assert len(all_refs) > 0

        # Check that we found the User schema references
        user_refs = [r for r in all_refs if "User" in r.ref]
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
        with pytest.raises(ValueError, match="Invalid array index"):
            resolver.resolve_reference("#/tags/invalid")

        # Out of bounds index
        with pytest.raises(ValueError, match="Invalid array index"):
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
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")

        user_schema = spec.resolve_reference("#/components/schemas/User")
        assert user_schema["type"] == "object"
        assert "username" in user_schema["properties"]

    def test_get_all_references_from_spec(self):
        """Test getting all references directly from the spec."""
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")

        all_refs = spec.get_all_references()
        assert len(all_refs) > 0
        assert all(isinstance(r, Reference) for r in all_refs)

        # All refs should be local in this fixture
        assert all(r.is_local for r in all_refs)

    def test_is_circular_reference_from_spec(self):
        """Test checking for circular references directly from the spec."""
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

        # The schema itself is not circular, but contains a circular reference
        assert spec.is_circular_reference("#/components/schemas/Node") is False

    def test_is_circular_reference_true(self):
        """Test detecting a truly circular reference."""
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

        # This creates a true circular chain
        assert spec.is_circular_reference("#/components/schemas/A") is True

    def test_resolve_reference_in_paths(self):
        """Test resolving references found in paths."""
        spec = parse_spec_from_file("tests/fixtures/petstore_openapi3.yaml")

        # Find a reference in the paths section
        all_refs = spec.get_all_references()
        path_refs = [r for r in all_refs if r.ref.endswith("/User")]

        assert len(path_refs) > 0

        # Resolve one of them
        resolved = spec.resolve_reference(path_refs[0])
        assert resolved["type"] == "object"
