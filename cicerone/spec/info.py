"""Info model for OpenAPI info object.

References:
- OpenAPI 3.x Info Object: https://spec.openapis.org/oas/v3.1.0#info-object
- OpenAPI 3.x Contact Object: https://spec.openapis.org/oas/v3.1.0#contact-object
- OpenAPI 3.x License Object: https://spec.openapis.org/oas/v3.1.0#license-object
"""

from typing import Any, Mapping

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """Represents contact information for the API."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    name: str | None = None
    url: str | None = None
    email: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Contact":
        """Create a Contact from a dictionary."""
        return cls(
            name=data.get("name"),
            url=data.get("url"),
            email=data.get("email"),
            **{k: v for k, v in data.items() if k not in {"name", "url", "email"}},
        )


class License(BaseModel):
    """Represents license information for the API."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    name: str
    url: str | None = None
    identifier: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "License":
        """Create a License from a dictionary."""
        return cls(
            name=data["name"],
            url=data.get("url"),
            identifier=data.get("identifier"),
            **{k: v for k, v in data.items() if k not in {"name", "url", "identifier"}},
        )


class Info(BaseModel):
    """Represents the Info object of an OpenAPI specification."""

    # Allow extra fields to support vendor extensions
    model_config = {"extra": "allow"}

    title: str
    version: str
    summary: str | None = None
    description: str | None = None
    terms_of_service: str | None = Field(None, alias="termsOfService")
    contact: Contact | None = None
    license: License | None = None

    def __str__(self) -> str:
        """Return a readable string representation of the info object."""
        parts = [f"'{self.title}' v{self.version}"]
        if self.description:
            desc_preview = self.description[:50] + "..." if len(self.description) > 50 else self.description
            parts.append(f"desc='{desc_preview}'")
        return f"<Info: {', '.join(parts)}>"

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Info":
        """Create an Info object from a dictionary."""
        contact = None
        if "contact" in data:
            contact = Contact.from_dict(data["contact"])

        license_obj = None
        if "license" in data:
            license_obj = License.from_dict(data["license"])

        return cls(
            title=data["title"],
            version=data["version"],
            summary=data.get("summary"),
            description=data.get("description"),
            termsOfService=data.get("termsOfService"),
            contact=contact,
            license=license_obj,
            **{
                k: v
                for k, v in data.items()
                if k not in {"title", "version", "summary", "description", "termsOfService", "contact", "license"}
            },
        )
