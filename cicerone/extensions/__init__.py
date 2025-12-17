"""OpenAPI extensions support.

This module provides support for OpenAPI vendor extensions (x-* fields).

OpenAPI specification allows for custom extensions that start with 'x-'.
These are commonly used by tools, vendors, and organizations to add
custom metadata or functionality to OpenAPI documents.

Common extensions found in real-world schemas:
- x-apisguru-categories: API categorization from APIs.guru
- x-logo: Logo URL for the API
- x-origin: Source information for the schema
- x-providerName: Name of the API provider
- x-serviceName: Name of the service
- x-maturity: Maturity level of the API

All Pydantic models in cicerone are configured with `extra="allow"`,
which means vendor extensions are automatically preserved in the model
instances. They can be accessed via standard attribute access or
through the `model_extra` property.

Example:
    >>> from cicerone.parse import parse_spec_from_file
    >>> spec = parse_spec_from_file("schema_with_extensions.yaml")
    >>> # Access extensions from raw dict
    >>> logo_url = spec.raw.get("info", {}).get("x-logo", {}).get("url")
    >>> # Extensions are preserved but not explicitly typed
    >>> maturity = spec.raw.get("x-maturity")

References:
- OpenAPI 3.x Specification Extensions: https://spec.openapis.org/oas/v3.1.0#specification-extensions
- Swagger 2.0 Vendor Extensions: https://swagger.io/specification/v2/#vendorExtensions
"""

from typing import Any

__all__ = ["get_extension", "has_extension"]


def get_extension(data: dict[str, Any], extension_name: str) -> Any | None:
    """Get an extension value from a data dictionary.

    Args:
        data: Dictionary containing potential extension fields
        extension_name: Name of the extension (with or without 'x-' prefix)

    Returns:
        The extension value if found, None otherwise

    Example:
        >>> data = {"x-custom": "value", "other": "data"}
        >>> get_extension(data, "custom")
        'value'
        >>> get_extension(data, "x-custom")
        'value'
    """
    # Ensure extension name starts with 'x-'
    if not extension_name.startswith("x-"):
        extension_name = f"x-{extension_name}"

    return data.get(extension_name)


def has_extension(data: dict[str, Any], extension_name: str) -> bool:
    """Check if an extension exists in a data dictionary.

    Args:
        data: Dictionary containing potential extension fields
        extension_name: Name of the extension (with or without 'x-' prefix)

    Returns:
        True if the extension exists, False otherwise

    Example:
        >>> data = {"x-custom": "value", "other": "data"}
        >>> has_extension(data, "custom")
        True
        >>> has_extension(data, "x-custom")
        True
        >>> has_extension(data, "missing")
        False
    """
    # Ensure extension name starts with 'x-'
    if not extension_name.startswith("x-"):
        extension_name = f"x-{extension_name}"

    return extension_name in data
