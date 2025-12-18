"""Tests for Version class."""

from cicerone.spec.version import Version


class TestVersion:
    """Tests for Version class."""

    def test_version_parsing_openapi3(self):
        """Test parsing OpenAPI 3.x version strings."""
        version = Version("3.0.0")
        assert version.major == 3
        assert version.minor == 0
        assert version.patch == 0
        assert version.raw == "3.0.0"
        assert str(version) == "3.0.0"

    def test_version_parsing_openapi31(self):
        """Test parsing OpenAPI 3.1.x version strings."""
        version = Version("3.1.0")
        assert version.major == 3
        assert version.minor == 1
        assert version.patch == 0

    def test_version_repr(self):
        """Test __repr__ method of Version."""
        version = Version("3.1.0")
        repr_str = repr(version)
        assert "Version" in repr_str
        assert "3.1.0" in repr_str
