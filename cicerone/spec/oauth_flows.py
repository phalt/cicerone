"""OAuthFlows model for OpenAPI OAuth flows.

References:
- OpenAPI 3.x OAuth Flows Object: https://spec.openapis.org/oas/v3.1.0#oauth-flows-object
- OpenAPI 3.x OAuth Flow Object: https://spec.openapis.org/oas/v3.1.0#oauth-flow-object
"""

from typing import Any

from pydantic import BaseModel, Field


class OAuthFlow(BaseModel):
    """Represents an OpenAPI OAuth Flow Object."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    authorizationUrl: str | None = None
    tokenUrl: str | None = None
    refreshUrl: str | None = None
    scopes: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OAuthFlow":
        """Create an OAuthFlow from a dictionary."""
        return cls(**data)


class OAuthFlows(BaseModel):
    """Represents an OpenAPI OAuth Flows Object."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    implicit: OAuthFlow | None = None
    password: OAuthFlow | None = None
    clientCredentials: OAuthFlow | None = None
    authorizationCode: OAuthFlow | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OAuthFlows":
        """Create an OAuthFlows from a dictionary."""
        flows_data: dict[str, Any] = {}

        if "implicit" in data:
            flows_data["implicit"] = OAuthFlow.from_dict(data["implicit"])
        if "password" in data:
            flows_data["password"] = OAuthFlow.from_dict(data["password"])
        if "clientCredentials" in data:
            flows_data["clientCredentials"] = OAuthFlow.from_dict(data["clientCredentials"])
        if "authorizationCode" in data:
            flows_data["authorizationCode"] = OAuthFlow.from_dict(data["authorizationCode"])

        # Add any extra fields
        for key, value in data.items():
            if key not in flows_data:
                flows_data[key] = value

        return cls(**flows_data)
