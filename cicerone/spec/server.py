"""Server model for OpenAPI server definitions.

References:
- OpenAPI 3.x Server Object: https://spec.openapis.org/oas/v3.1.0#server-object
- OpenAPI 3.x Server Variable Object: https://spec.openapis.org/oas/v3.1.0#server-variable-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils


class ServerVariable(pydantic.BaseModel):
    """Represents a server variable for use in server URL template substitution."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    enum: list[str] = pydantic.Field(default_factory=list)
    default: str
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> ServerVariable:
        """Create a ServerVariable from a dictionary."""
        excluded = {"enum", "default", "description"}
        return cls(
            enum=data.get("enum", []),
            default=data["default"],
            description=data.get("description"),
            **{k: v for k, v in data.items() if k not in excluded},
        )


class Server(pydantic.BaseModel):
    """Represents an OpenAPI Server object."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    url: str
    description: str | None = None
    variables: dict[str, ServerVariable] = pydantic.Field(default_factory=dict)

    def __str__(self) -> str:
        """Return a readable string representation of the server."""
        parts = [f"url={self.url}"]
        if self.description:
            parts.append(f"'{self.description}'")
        if self.variables:
            parts.append(f"{len(self.variables)} variables")
        return f"<Server: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Server:
        """Create a Server from a dictionary."""
        excluded = {"url", "description", "variables"}
        return cls(
            url=data["url"],
            description=data.get("description"),
            variables=model_utils.parse_collection(data, "variables", ServerVariable.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
