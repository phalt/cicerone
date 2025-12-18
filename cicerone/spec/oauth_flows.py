"""OAuthFlows model for OpenAPI OAuth flows.

References:
- OpenAPI 3.x OAuth Flows Object: https://spec.openapis.org/oas/v3.1.0#oauth-flows-object
- OpenAPI 3.x OAuth Flow Object: https://spec.openapis.org/oas/v3.1.0#oauth-flow-object
"""

from __future__ import annotations


import typing

import pydantic

from cicerone.spec import model_utils


class oauth_flows.OAuthFlow(pydantic.BaseModel):
    """Represents an OpenAPI OAuth Flow Object."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    authorizationUrl: str | None = None
    tokenUrl: str | None = None
    refreshUrl: str | None = None
    scopes: dict[str, str] = pydantic.Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "oauth_flows.OAuthFlow":
        """Create an oauth_flows.OAuthFlow from a dictionary."""
        # Simple passthrough - pydantic handles all fields with extra="allow"
        return cls(**data)


class OAuthFlows(pydantic.BaseModel):
    """Represents an OpenAPI OAuth Flows Object."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    implicit: oauth_flows.OAuthFlow | None = None
    password: oauth_flows.OAuthFlow | None = None
    clientCredentials: oauth_flows.OAuthFlow | None = None
    authorizationCode: oauth_flows.OAuthFlow | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "OAuthFlows":
        """Create an OAuthFlows from a dictionary."""
        excluded = {"implicit", "password", "clientCredentials", "authorizationCode"}
        return cls(
            implicit=model_utils.parse_nested_object(data, "implicit", OAuthFlow.from_dict),
            password=model_utils.parse_nested_object(data, "password", OAuthFlow.from_dict),
            clientCredentials=model_utils.parse_nested_object(data, "clientCredentials", OAuthFlow.from_dict),
            authorizationCode=model_utils.parse_nested_object(data, "authorizationCode", OAuthFlow.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
