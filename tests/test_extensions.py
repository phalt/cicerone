"""Tests for OpenAPI extensions support."""

from cicerone.extensions import get_extension, has_extension


class TestExtensions:
    """Test extension utility functions."""

    def test_get_extension_with_prefix(self) -> None:
        """Test getting extension value with x- prefix."""
        data = {"x-custom": "value", "other": "data"}
        assert get_extension(data, "x-custom") == "value"

    def test_get_extension_without_prefix(self) -> None:
        """Test getting extension value without x- prefix."""
        data = {"x-custom": "value", "other": "data"}
        assert get_extension(data, "custom") == "value"

    def test_get_extension_missing(self) -> None:
        """Test getting missing extension returns None."""
        data = {"other": "data"}
        assert get_extension(data, "custom") is None

    def test_has_extension_with_prefix(self) -> None:
        """Test checking extension existence with x- prefix."""
        data = {"x-custom": "value", "other": "data"}
        assert has_extension(data, "x-custom") is True

    def test_has_extension_without_prefix(self) -> None:
        """Test checking extension existence without x- prefix."""
        data = {"x-custom": "value", "other": "data"}
        assert has_extension(data, "custom") is True

    def test_has_extension_missing(self) -> None:
        """Test checking missing extension returns False."""
        data = {"other": "data"}
        assert has_extension(data, "missing") is False

    def test_get_extension_dict_value(self) -> None:
        """Test getting extension with dictionary value."""
        data = {"x-logo": {"url": "https://example.com/logo.png"}}
        logo = get_extension(data, "logo")
        assert logo == {"url": "https://example.com/logo.png"}
        assert logo["url"] == "https://example.com/logo.png"

    def test_get_extension_list_value(self) -> None:
        """Test getting extension with list value."""
        data = {"x-categories": ["api", "cloud"]}
        categories = get_extension(data, "categories")
        assert categories == ["api", "cloud"]
