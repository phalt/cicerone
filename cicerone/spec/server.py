"""Server model for OpenAPI server definitions.

References:
- OpenAPI 3.x Server Object: https://spec.openapis.org/oas/v3.1.0#server-object
- OpenAPI 3.x Server Variable Object: https://spec.openapis.org/oas/v3.1.0#server-variable-object
"""

from typing import Any, Mapping

from pydantic import BaseModel, Field


class ServerVariable(BaseModel):
    """Represents a server variable for use in server URL template substitution."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    enum: list[str] = Field(default_factory=list)
    default: str
    description: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ServerVariable":
        """Create a ServerVariable from a dictionary."""
        return cls(
            enum=data.get("enum", []),
            default=data["default"],
            description=data.get("description"),
            **{k: v for k, v in data.items() if k not in {"enum", "default", "description"}},
        )


class Server(BaseModel):
    """Represents an OpenAPI Server object."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    url: str
    description: str | None = None
    variables: dict[str, ServerVariable] = Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of the server."""
        parts = [f"url={self.url}"]
        if self.description:
            parts.append(f"'{self.description}'")
        if self.variables:
            parts.append(f"{len(self.variables)} variables")
        return f"<Server: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Server":
        """Create a Server from a dictionary."""
        variables = {}
        if "variables" in data:
            for name, var_data in data["variables"].items():
                variables[name] = ServerVariable.from_dict(var_data)

        return cls(
            url=data["url"],
            description=data.get("description"),
            variables=variables,
            **{k: v for k, v in data.items() if k not in {"url", "description", "variables"}},
        )
