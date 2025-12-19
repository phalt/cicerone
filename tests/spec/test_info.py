"""Tests for Info model."""

from __future__ import annotations

from cicerone import spec as cicerone_spec


class TestContact:
    """Tests for Contact model."""

    def test_contact_from_dict(self):
        """Test creating Contact from dict."""
        data = {
            "name": "API Team",
            "url": "https://example.com",
            "email": "api@example.com",
        }
        contact = cicerone_spec.Contact.from_dict(data)
        assert contact.name == "API Team"
        assert contact.url == "https://example.com"
        assert contact.email == "api@example.com"

    def test_contact_partial_data(self):
        """Test creating Contact with partial data."""
        data = {"name": "API Team"}
        contact = cicerone_spec.Contact.from_dict(data)
        assert contact.name == "API Team"
        assert contact.url is None
        assert contact.email is None

    def test_contact_empty_dict(self):
        """Test creating Contact from empty dict."""
        data: dict[str, str] = {}
        contact = cicerone_spec.Contact.from_dict(data)
        assert contact.name is None
        assert contact.url is None
        assert contact.email is None


class TestLicense:
    """Tests for License model."""

    def test_license_from_dict(self):
        """Test creating License from dict."""
        data = {
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        }
        license = cicerone_spec.License.from_dict(data)
        assert license.name == "Apache 2.0"
        assert license.url == "https://www.apache.org/licenses/LICENSE-2.0.html"

    def test_license_with_identifier(self):
        """Test creating License with identifier (OpenAPI 3.1)."""
        data = {
            "name": "MIT",
            "identifier": "MIT",
        }
        license = cicerone_spec.License.from_dict(data)
        assert license.name == "MIT"
        assert license.identifier == "MIT"


class TestInfo:
    """Tests for Info model."""

    def test_info_minimal(self):
        """Test creating minimal Info object."""
        data = {
            "title": "Test API",
            "version": "1.0.0",
        }
        info = cicerone_spec.Info.from_dict(data)
        assert info.title == "Test API"
        assert info.version == "1.0.0"
        assert info.summary is None
        assert info.description is None

    def test_info_complete(self):
        """Test creating complete Info object."""
        data = {
            "title": "Test API",
            "version": "1.0.0",
            "summary": "A test API",
            "description": "This is a test API for testing purposes",
            "termsOfService": "https://example.com/terms",
            "contact": {
                "name": "API Team",
                "email": "api@example.com",
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            },
        }
        info = cicerone_spec.Info.from_dict(data)
        assert info.title == "Test API"
        assert info.version == "1.0.0"
        assert info.summary == "A test API"
        assert info.description == "This is a test API for testing purposes"
        assert info.terms_of_service == "https://example.com/terms"
        assert info.contact is not None
        assert info.contact.name == "API Team"
        assert info.license is not None
        assert info.license.name == "MIT"

    def test_info_str_representation(self):
        """Test __str__ method of Info."""
        data = {
            "title": "Test API",
            "version": "1.0.0",
        }
        info = cicerone_spec.Info.from_dict(data)
        str_repr = str(info)
        assert "<Info:" in str_repr
        assert "Test API" in str_repr
        assert "v1.0.0" in str_repr

    def test_info_str_with_description(self):
        """Test __str__ method with description."""
        data = {
            "title": "Test API",
            "version": "1.0.0",
            "description": "A test API for testing",
        }
        info = cicerone_spec.Info.from_dict(data)
        str_repr = str(info)
        assert "<Info:" in str_repr
        assert "desc=" in str_repr

    def test_info_str_with_long_description(self):
        """Test __str__ method with long description (should be truncated)."""
        data = {
            "title": "Test API",
            "version": "1.0.0",
            "description": "A" * 100,  # Very long description
        }
        info = cicerone_spec.Info.from_dict(data)
        str_repr = str(info)
        assert "..." in str_repr  # Should be truncated
        assert len(str_repr) < 200  # Should not be too long
