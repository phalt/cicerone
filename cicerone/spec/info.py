"""info.Info model for OpenAPI info object.

References:
- OpenAPI 3.x info.Info Object: https://spec.openapis.org/oas/v3.1.0#info-object
- OpenAPI 3.x info.Contact Object: https://spec.openapis.org/oas/v3.1.0#contact-object
- OpenAPI 3.x info.License Object: https://spec.openapis.org/oas/v3.1.0#license-object
"""

from __future__ import annotations

import typing

import pydantic

from cicerone.spec import model_utils


class info.Contact(pydantic.BaseModel):
    """Represents contact information for the API."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    name: str | None = None
    url: str | None = None
    email: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> info.Contact:
        """Create a info.Contact from a dictionary."""
        excluded = {"name", "url", "email"}
        return cls(
            name=data.get("name"),
            url=data.get("url"),
            email=data.get("email"),
            **{k: v for k, v in data.items() if k not in excluded},
        )


class info.License(pydantic.BaseModel):
    """Represents license information for the API."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    name: str
    url: str | None = None
    identifier: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> info.License:
        """Create a info.License from a dictionary."""
        excluded = {"name", "url", "identifier"}
        return cls(
            name=data["name"],
            url=data.get("url"),
            identifier=data.get("identifier"),
            **{k: v for k, v in data.items() if k not in excluded},
        )


class info.Info(pydantic.BaseModel):
    """Represents the info.Info object of an OpenAPI specification."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    title: str
    version: str
    summary: str | None = None
    description: str | None = None
    terms_of_service: "str | None" = pydantic.Field(None, alias="termsOfService")
    contact: info.Contact | None = None
    license: info.License | None = None

    def __str__(self) -> str:
        """Return a readable string representation of the info object."""
        parts = [f"'{self.title}' v{self.version}"]
        if self.description:
            desc_preview = self.description[:50] + "..." if len(self.description) > 50 else self.description
            parts.append(f"desc='{desc_preview}'")
        return f"<info.Info: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> info.Info:
        """Create an info.Info object from a dictionary."""
        excluded = {"title", "version", "summary", "description", "termsOfService", "contact", "license"}
        return cls(
            title=data["title"],
            version=data["version"],
            summary=data.get("summary"),
            description=data.get("description"),
            termsOfService=data.get("termsOfService"),
            contact=model_utils.parse_nested_object(data, "contact", Contact.from_dict),
            license=model_utils.parse_nested_object(data, "license", License.from_dict),
            **{k: v for k, v in data.items() if k not in excluded},
        )
