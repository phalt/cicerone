"""Tests for Tag and ExternalDocumentation models."""

from __future__ import annotations

from cicerone import spec as cicerone_spec


class TestExternalDocumentation:
    """Tests for ExternalDocumentation model."""

    def test_external_docs_from_dict(self):
        """Test creating ExternalDocumentation from dict."""
        data = {
            "url": "https://docs.example.com",
            "description": "External documentation",
        }
        ext_docs = cicerone_spec.ExternalDocumentation.from_dict(data)
        assert ext_docs.url == "https://docs.example.com"
        assert ext_docs.description == "External documentation"

    def test_external_docs_minimal(self):
        """Test creating ExternalDocumentation with only URL."""
        data = {"url": "https://docs.example.com"}
        ext_docs = cicerone_spec.ExternalDocumentation.from_dict(data)
        assert ext_docs.url == "https://docs.example.com"
        assert ext_docs.description is None


class TestTag:
    """Tests for Tag model."""

    def test_tag_minimal(self):
        """Test creating minimal Tag."""
        data = {"name": "users"}
        tag = cicerone_spec.Tag.from_dict(data)
        assert tag.name == "users"
        assert tag.description is None
        assert tag.external_docs is None

    def test_tag_with_description(self):
        """Test creating Tag with description."""
        data = {
            "name": "users",
            "description": "User management endpoints",
        }
        tag = cicerone_spec.Tag.from_dict(data)
        assert tag.name == "users"
        assert tag.description == "User management endpoints"

    def test_tag_with_external_docs(self):
        """Test creating Tag with external documentation."""
        data = {
            "name": "users",
            "externalDocs": {
                "url": "https://docs.example.com/users",
                "description": "User documentation",
            },
        }
        tag = cicerone_spec.Tag.from_dict(data)
        assert tag.name == "users"
        assert tag.external_docs is not None
        assert tag.external_docs.url == "https://docs.example.com/users"
        assert tag.external_docs.description == "User documentation"

    def test_tag_str_representation(self):
        """Test __str__ method of Tag."""
        data = {"name": "users"}
        tag = cicerone_spec.Tag.from_dict(data)
        str_repr = str(tag)
        assert "<Tag:" in str_repr
        assert "name='users'" in str_repr

    def test_tag_str_with_description(self):
        """Test __str__ method with description."""
        data = {
            "name": "users",
            "description": "User endpoints",
        }
        tag = cicerone_spec.Tag.from_dict(data)
        str_repr = str(tag)
        assert "desc=" in str_repr
        assert "User endpoints" in str_repr

    def test_tag_str_with_long_description(self):
        """Test __str__ method with long description (should be truncated)."""
        data = {
            "name": "users",
            "description": "A" * 100,  # Very long description
        }
        tag = cicerone_spec.Tag.from_dict(data)
        str_repr = str(tag)
        assert "..." in str_repr  # Should be truncated
        assert len(str_repr) < 150  # Should not be too long
