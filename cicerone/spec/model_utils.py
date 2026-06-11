"""Utility functions for model parsing.

This module provides reusable helpers for parsing OpenAPI specification data
into model objects, including nested object parsing and collection handling.
"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import pydantic

T = typing.TypeVar("T")


def mirror_extras(
    obj: pydantic.BaseModel,
    data: typing.Mapping[str, typing.Any],
    keys: typing.Iterable[str],
) -> None:
    """Mirror raw source values into a model's ``__pydantic_extra__``.

    .. deprecated:: 0.4.0
        This is a compatibility shim for consumers that accessed spec fields via
        ``model_extra`` before they were promoted to typed model fields in 0.4.0.
        The mirrored copies will be removed in 0.5.0 - use the typed fields instead.

    Once a key is declared as a typed field, Pydantic routes it to the field and it
    no longer appears in ``__pydantic_extra__``. This helper re-injects the raw
    source values (not the parsed models) so that pre-0.4.0 access patterns like
    ``schema.model_extra.get("enum")`` keep returning the same data.

    Args:
        obj: The freshly constructed model to mirror values onto
        data: The raw source dictionary the model was parsed from
        keys: The wire-format keys (e.g. "$ref", "requestBody") to mirror
    """
    extra = obj.__pydantic_extra__
    if extra is None:
        return
    for key in keys:
        if key in data and key not in extra:
            extra[key] = data[key]


def truncate_text(text: str, max_len: int = 50) -> str:
    """Truncate text with ellipsis if it exceeds max length.

    Args:
        text: Text to truncate
        max_len: Maximum length before truncation

    Returns:
        Truncated text with '...' appended if needed

    Example:
        truncate_text("A very long description...", 20)
    """
    return text if len(text) <= max_len else f"{text[:max_len]}..."


def parse_nested_object(
    data: typing.Mapping[str, typing.Any],
    field_name: str,
    parser_func: typing.Callable[[dict[str, typing.Any]], T],
) -> T | None:
    """Parse a nested object field if it exists.

    Args:
        data: Source dictionary
        field_name: Name of field containing nested object
        parser_func: Function to parse the nested object (usually Class.from_dict)

    Returns:
        Parsed object or None if field doesn't exist

    Example:
        parse_nested_object(data, "schema", Schema.from_dict)
    """
    if field_name in data:
        return parser_func(data[field_name])
    return None


def parse_collection(
    data: typing.Mapping[str, typing.Any],
    field_name: str,
    parser_func: typing.Callable[[dict[str, typing.Any]], T],
) -> dict[str, T]:
    """Parse a collection of objects into a dictionary.

    Args:
        data: Source dictionary
        field_name: Name of field containing the collection
        parser_func: Function to parse each item (usually Class.from_dict)

    Returns:
        Dictionary mapping names to parsed objects, empty dict if field doesn't exist

    Example:
        parse_collection(data, "examples", Example.from_dict)
    """
    if field_name in data:
        return {name: parser_func(item_data) for name, item_data in data[field_name].items()}
    return {}


def parse_list(
    data: typing.Mapping[str, typing.Any],
    field_name: str,
    parser_func: typing.Callable[[dict[str, typing.Any]], T],
) -> list[T]:
    """Parse a list of objects.

    Args:
        data: Source dictionary
        field_name: Name of field containing the list
        parser_func: Function to parse each item (usually Class.from_dict)

    Returns:
        List of parsed objects, empty list if field doesn't exist

    Example:
        parse_list(data, "servers", Server.from_dict)
    """
    if field_name in data and isinstance(data[field_name], list):
        return [parser_func(item_data) for item_data in data[field_name]]
    return []


def parse_list_or_none(
    data: typing.Mapping[str, typing.Any],
    field_name: str,
    parser_func: typing.Callable[[dict[str, typing.Any]], T],
) -> list[T] | None:
    """Parse a list of objects, returning None if field doesn't exist.

    Note: This function filters out non-dict items before parsing, which is useful
    for schema composition keywords that should only contain object definitions.
    This differs from parse_list() which processes all items.

    Args:
        data: Source dictionary
        field_name: Name of field containing the list
        parser_func: Function to parse each item (usually Class.from_dict)

    Returns:
        List of parsed objects, or None if field doesn't exist

    Example:
        parse_list_or_none(data, "allOf", Schema.from_dict)
    """
    if field_name in data and isinstance(data[field_name], list):
        return [parser_func(item_data) for item_data in data[field_name] if isinstance(item_data, dict)]
    return None
