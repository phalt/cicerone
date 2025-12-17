"""Paths container model for all path items."""

from typing import Any, Generator, Mapping

from pydantic import BaseModel, Field

from cicerone.spec.operation import Operation
from cicerone.spec.path_item import PathItem


class Paths(BaseModel):
    """Container for all path items in the spec."""

    model_config = {"extra": "allow"}

    items: dict[str, PathItem] = Field(default_factory=dict)

    def __getitem__(self, path: str) -> PathItem:
        """Get a path item by path string."""
        return self.items[path]

    def __contains__(self, path: str) -> bool:
        """Check if a path exists."""
        return path in self.items

    def all_operations(self) -> Generator[Operation, None, None]:
        """Yield all operations across all paths."""
        for path_item in self.items.values():
            yield from path_item.operations.values()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Paths":
        """Create Paths from a dictionary."""
        items = {}
        for path, path_data in data.items():
            if isinstance(path_data, dict):
                items[path] = PathItem.from_dict(path, path_data)
        return cls(items=items)
