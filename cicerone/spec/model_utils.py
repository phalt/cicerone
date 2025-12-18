"""Utility functions for model parsing.

This module provides reusable helpers for parsing OpenAPI specification data
into model objects, including nested object parsing and collection handling.
"""

from __future__ import annotations


from typing import Any, Callable, Mapping, TypeVar

T = TypeVar("T")


def parse_nested_object(
    data: Mapping[str, Any],
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
    data: Mapping[str, Any],
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


def parse_list(
    data: Mapping[str, Any],
    field_name: str,
    parser: Callable[[dict[str, Any]], T],
) -> list[T]:
    """Parse a list of objects.

    Args:
        data: Source dictionary
        field_name: Name of field containing the list
        parser: Function to parse each item (usually Class.from_dict)

    Returns:
        List of parsed objects, empty list if field doesn't exist

    Example:
        parse_list(data, "servers", Server.from_dict)
    """
    if field_name in data and isinstance(data[field_name], list):
        return [parser(item_data) for item_data in data[field_name]]
    return []
