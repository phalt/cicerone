"""Callback model for OpenAPI callbacks.

References:
- OpenAPI 3.x Callback Object: https://spec.openapis.org/oas/v3.1.0#callback-object

A Callback Object is a map of possible out-of-band requests and responses
that may be initiated by the API provider and expected to be handled by the API consumer.
The key is a runtime expression that identifies a URL to use for the callback operation.
The value is a Path Item Object or a reference to one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from cicerone.spec.path_item import PathItem


class Callback(BaseModel):
    """Represents an OpenAPI Callback Object.

    A callback is a map of runtime expressions to Path Item Objects.
    Each runtime expression defines a URL where a callback request will be sent.
    """

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    # Callbacks are a dict of expression -> PathItem
    expressions: dict[str, PathItem] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Callback:
        """Create a Callback from a dictionary.

        Args:
            data: Dictionary containing callback expressions mapping to Path Items

        Returns:
            Callback object with expressions parsed as PathItem objects
        """
        from cicerone.spec.path_item import PathItem

        # Parse each expression as a PathItem
        expressions: dict[str, PathItem] = {}
        for expression, path_item_data in data.items():
            expressions[expression] = PathItem.from_dict(expression, path_item_data)

        return cls(expressions=expressions)

    def get(self, expression: str) -> PathItem | None:
        """Get a PathItem for a given expression.

        Args:
            expression: The runtime expression (e.g., '{$request.body#/callbackUrl}')

        Returns:
            PathItem if found, None otherwise
        """
        return self.expressions.get(expression)
