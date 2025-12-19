"""Callback model for OpenAPI callbacks.

References:
- OpenAPI 3.x Callback Object: https://spec.openapis.org/oas/v3.1.0#callback-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import path_item as spec_path_item


class Callback(pydantic.BaseModel):
    """Represents an OpenAPI Callback Object.

    A callback is a map of runtime expressions to Path Item Objects.
    Each runtime expression defines a URL where a callback request will be sent.
    """

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    # Callbacks are a dict of expression -> PathItem
    expressions: dict[str, spec_path_item.PathItem] = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Callback:
        """Create a Callback from a dictionary.

        Args:
            data: Dictionary containing callback expressions mapping to Path Items

        Returns:
            Callback object with expressions parsed as PathItem objects
        """
        # Parse each expression as a PathItem
        expressions: dict[str, spec_path_item.PathItem] = {}
        for expression, path_item_data in data.items():
            expressions[expression] = spec_path_item.PathItem.from_dict(expression, path_item_data)

        return cls(expressions=expressions)

    def get(self, expression: str) -> spec_path_item.PathItem | None:
        """Get a PathItem for a given expression.

        Args:
            expression: The runtime expression (e.g., '{$request.body#/callbackUrl}')

        Returns:
            PathItem if found, None otherwise
        """
        return self.expressions.get(expression)
