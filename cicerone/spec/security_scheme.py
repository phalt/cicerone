"""SecurityScheme model for OpenAPI security schemes.

References:
- OpenAPI 3.x Security Scheme Object: https://spec.openapis.org/oas/v3.1.0#security-scheme-object
"""

from typing import Any

from pydantic import BaseModel
from pydantic import Field

from cicerone.spec import model_utils
from cicerone.spec import oauth_flows as oauth_flows_module

# Extract classes for type annotations
OAuthFlows = oauth_flows_module.OAuthFlows


class SecurityScheme(BaseModel):
    """Represents an OpenAPI security scheme object."""

    # Allow extra fields to support vendor extensions and future spec additions
    model_config = {"extra": "allow"}

    type: str | None = None
    description: str | None = None
    name: str | None = None
    in_: str | None = Field(None, alias="in")
    scheme: str | None = None
    bearerFormat: str | None = Field(None, alias="bearerFormat")
    flows: OAuthFlows | None = None
    openIdConnectUrl: str | None = Field(None, alias="openIdConnectUrl")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SecurityScheme":
        """Create a SecurityScheme from a dictionary."""
        excluded = {"type", "description", "name", "in", "scheme", "bearerFormat", "flows", "openIdConnectUrl"}
        return cls(
            type=data.get("type"),
            description=data.get("description"),
            name=data.get("name"),
            **{"in": data.get("in")},
            scheme=data.get("scheme"),
            bearerFormat=data.get("bearerFormat"),
            flows=model_utils.parse_nested_object(data, "flows", oauth_flows_module.OAuthFlows.from_dict),
            openIdConnectUrl=data.get("openIdConnectUrl"),
            **{k: v for k, v in data.items() if k not in excluded},
        )
