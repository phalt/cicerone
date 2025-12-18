"""Webhooks model for OpenAPI 3.1 webhook definitions.

References:
- OpenAPI 3.1.x Webhooks: https://spec.openapis.org/oas/v3.1.0#fixed-fields
"""

from typing import Any, Generator, Mapping

from pydantic import BaseModel, Field

from cicerone.spec.operation import Operation
from cicerone.spec.path_item import PathItem


class Webhooks(BaseModel):
    """Container for webhook definitions (OpenAPI 3.1+)."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    items: dict[str, PathItem] = Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of webhooks."""
        if not self.items:
            return "<Webhooks: empty>"
        webhook_list = ", ".join(list(self.items.keys())[:3])
        if len(self.items) > 3:
            webhook_list += f" (+{len(self.items) - 3} more)"
        return f"<Webhooks: {len(self.items)} webhooks [{webhook_list}]>"

    def all_operations(self) -> Generator[Operation, None, None]:
        """Yield all operations across all webhooks.

        Yields:
            Operation objects
        """
        for webhook_name, path_item in self.items.items():
            for operation in path_item.operations.values():
                yield operation

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Webhooks":
        """Create Webhooks from a dictionary of webhook definitions."""
        items = {}
        for webhook_name, webhook_data in data.items():
            # Each webhook is like a PathItem but without a path
            # We'll use the webhook name as the "path" for consistency
            items[webhook_name] = PathItem.from_dict(f"webhook:{webhook_name}", webhook_data)
        return cls(items=items)
