"""Operation model for HTTP operations.

References:
- OpenAPI 3.x Operation Object: https://spec.openapis.org/oas/v3.1.0#operation-object
"""

from typing import Any, ClassVar, Mapping

from pydantic import BaseModel, Field


class Operation(BaseModel):
    """Represents an HTTP operation (GET, POST, etc.)."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    # Fields that are explicitly mapped in from_dict() to avoid double-processing
    EXPLICITLY_MAPPED_FIELDS: ClassVar[set[str]] = {
        "operationId",
        "summary",
        "description",
        "tags",
        "parameters",
        "responses",
    }

    method: str
    path: str
    operation_id: str | None = Field(None, alias="operationId")
    summary: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[Any] = Field(default_factory=list)
    responses: dict[str, Any] = Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of the operation."""
        parts = [f"{self.method} {self.path}"]
        if self.operation_id:
            parts.append(f"id={self.operation_id}")
        if self.summary:
            parts.append(f"'{self.summary}'")
        if self.tags:
            parts.append(f"tags={self.tags}")
        return f"<Operation: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, method: str, path: str, data: Mapping[str, Any]) -> "Operation":
        """Create an Operation from a dictionary."""
        return cls(
            method=method,
            path=path,
            operationId=data.get("operationId"),
            summary=data.get("summary"),
            description=data.get("description"),
            tags=data.get("tags", []),
            parameters=data.get("parameters", []),
            responses=data.get("responses", {}),
            **{k: v for k, v in data.items() if k not in cls.EXPLICITLY_MAPPED_FIELDS},
        )
