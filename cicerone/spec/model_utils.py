"""Utility functions for model parsing to reduce code duplication.

This module provides common patterns used across model from_dict() methods,
centralizing field extraction, nested object parsing, and collection handling.
"""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def extract_fields(data: dict[str, Any], *field_names: str, **field_defaults: Any) -> dict[str, Any]:
    """Extract multiple fields from a data dictionary.

    Args:
        data: Source dictionary
        *field_names: Field names to extract (will use None as default)
        **field_defaults: Field names with their default values

    Returns:
        Dictionary with extracted fields

    Example:
        extract_fields(data, "name", "type", required=False, description=None)
    """
    result = {}
    for field in field_names:
        result[field] = data.get(field)
    for field, default in field_defaults.items():
        result[field] = data.get(field, default)
    return result


def parse_nested_object(
    data: dict[str, Any],
    field_name: str,
    parser: Callable[[dict[str, Any]], T],
) -> T | None:
    """Parse a nested object field if it exists.

    Args:
        data: Source dictionary
        field_name: Name of field containing nested object
        parser: Function to parse the nested object (usually Class.from_dict)

    Returns:
        Parsed object or None if field doesn't exist

    Example:
        parse_nested_object(data, "schema", Schema.from_dict)
    """
    if field_name in data:
        return parser(data[field_name])
    return None


def parse_collection(
    data: dict[str, Any],
    field_name: str,
    parser: Callable[[dict[str, Any]], T],
) -> dict[str, T]:
    """Parse a collection of objects into a dictionary.

    Args:
        data: Source dictionary
        field_name: Name of field containing the collection
        parser: Function to parse each item (usually Class.from_dict)

    Returns:
        Dictionary mapping names to parsed objects, empty dict if field doesn't exist

    Example:
        parse_collection(data, "examples", Example.from_dict)
    """
    if field_name in data:
        return {name: parser(item_data) for name, item_data in data[field_name].items()}
    return {}


def add_extra_fields(
    result: dict[str, Any],
    data: dict[str, Any],
    exclude: set[str] | None = None,
) -> None:
    """Add any fields from data not already in result (for extra/vendor fields).

    Args:
        result: Target dictionary to update (modified in place)
        data: Source dictionary
        exclude: Optional set of field names to exclude from adding

    Example:
        result = {"name": "foo"}
        add_extra_fields(result, data, exclude={"name", "type"})
    """
    exclude = exclude or set()
    for key, value in data.items():
        if key not in result and key not in exclude:
            result[key] = value
