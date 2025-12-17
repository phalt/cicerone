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

    def test_version_parsing_swagger2(self):
        """Test parsing Swagger 2.0 version strings."""
        version = Version("2.0")
        assert version.major == 2
        assert version.minor == 0
        assert version.patch == 0
