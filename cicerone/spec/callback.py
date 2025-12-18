"""Callback model for OpenAPI callbacks.

References:
- OpenAPI 3.x Callback Object: https://spec.openapis.org/oas/v3.1.0#callback-object

A Callback Object is a map of possible out-of-band requests and responses
that may be initiated by the API provider and expected to be handled by the API consumer.
The key is a runtime expression that identifies a URL to use for the callback operation.
The value is a Path Item Object or a reference to one.
"""

from typing import Any

from pydantic import BaseModel, Field


class Callback(BaseModel):
    """Represents an OpenAPI Callback Object.

    A callback is a map of runtime expressions to Path Item Objects.
    Each runtime expression defines a URL where a callback request will be sent.
    """

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    # Callbacks are essentially a dict of expression -> PathItem
    # We store them as dict[str, Any] for now since PathItem can be complex
    expressions: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Callback":
        """Create a Callback from a dictionary.

        Args:
            data: Dictionary containing callback expressions mapping to Path Items

        Returns:
            Callback object with expressions stored
        """
        # The entire data dict represents the callback expressions
        return cls(expressions=data)

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to expressions."""
        return self.expressions.get(key)

    def __contains__(self, key: str) -> bool:
        """Check if expression exists."""
        return key in self.expressions

    def items(self):
        """Return items for iteration."""
        return self.expressions.items()

    def keys(self):
        """Return keys for iteration."""
        return self.expressions.keys()

    def values(self):
        """Return values for iteration."""
        return self.expressions.values()
