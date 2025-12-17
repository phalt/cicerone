"""Operation model for HTTP operations."""

from typing import Any, ClassVar, Mapping

from pydantic import BaseModel, Field


class Operation(BaseModel):
    """Represents an HTTP operation (GET, POST, etc.)."""

    model_config = {"extra": "allow"}

    # Fields that are explicitly handled
    HANDLED_FIELDS: ClassVar[set[str]] = {"operationId", "summary", "description", "tags", "parameters", "responses"}

    method: str
    path: str
    operation_id: str | None = Field(None, alias="operationId")
    summary: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[Any] = Field(default_factory=list)
    responses: dict[str, Any] = Field(default_factory=dict)

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
            **{k: v for k, v in data.items() if k not in cls.HANDLED_FIELDS},
        )
