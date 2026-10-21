"""How each OpenAPI object maps onto cicerone's models, for the conformance tests.

This is the explicit mapping table the field-coverage test checks against.
Keep it honest: an object cicerone does not model yet maps to None, so its
fields show up as gaps instead of passing silently.
"""

from __future__ import annotations

import typing

import pydantic

import cicerone
from cicerone.spec import path_item as spec_path_item

# Objects with a model class whose wire field names come from model aliases
MODELS: dict[str, type[pydantic.BaseModel] | None] = {
    "OpenAPI Object": cicerone.OpenAPISpec,
    "Info Object": cicerone.Info,
    "Contact Object": cicerone.Contact,
    "License Object": cicerone.License,
    "Server Object": cicerone.Server,
    "Server Variable Object": cicerone.ServerVariable,
    "Components Object": cicerone.Components,
    "Paths Object": cicerone.Paths,
    "Path Item Object": cicerone.PathItem,
    "Operation Object": cicerone.Operation,
    "External Documentation Object": cicerone.ExternalDocumentation,
    "Parameter Object": cicerone.Parameter,
    "Request Body Object": cicerone.RequestBody,
    "Media Type Object": cicerone.MediaType,
    "Encoding Object": cicerone.Encoding,
    "Response Object": cicerone.Response,
    "Callback Object": cicerone.Callback,
    "Example Object": cicerone.Example,
    "Link Object": cicerone.Link,
    "Header Object": cicerone.Header,
    "Tag Object": cicerone.Tag,
    "Reference Object": cicerone.Reference,
    "Schema Object": cicerone.Schema,
    "Discriminator Object": cicerone.Discriminator,
    "Security Scheme Object": cicerone.SecurityScheme,
    "OAuth Flows Object": cicerone.OAuthFlows,
    "OAuth Flow Object": cicerone.OAuthFlow,
    # Not modelled yet (spec Task 15 adds it)
    "XML Object": None,
    # Plain maps in cicerone by design: Operation.responses is dict[str, Response]
    # and security requirements are dict[str, list[str]]
    "Responses Object": None,
    "Security Requirement Object": None,
}

# Fields covered by something other than a same-named model field. Each entry
# says what covers it; keep this list short and justified.
COVERED_ELSEWHERE: dict[tuple[str, str], str] = {
    ("OpenAPI Object", "openapi"): "OpenAPISpec.version",
    ("Reference Object", "$ref"): "Reference.ref (validator accepts $ref)",
    ("Responses Object", "default"): "Operation.responses key 'default'",
    **{("Path Item Object", method): "PathItem.operations" for method in spec_path_item.HTTP_METHODS},
}


def wire_names(model: type[pydantic.BaseModel]) -> set[str]:
    """Every name a model field accepts from the wire: its alias if any, else its name."""
    return {info.alias or name for name, info in model.model_fields.items()}


def is_field_covered(object_name: str, field: str) -> bool:
    if (object_name, field) in COVERED_ELSEWHERE:
        return True
    model = MODELS.get(object_name)
    return model is not None and field in wire_names(model)


_SECURITY_REQUIREMENT = pydantic.TypeAdapter(dict[str, list[str]])

# Sections whose examples show some other object using this one: the
# Discriminator and XML sections illustrate them with Schema Objects
EXAMPLE_OBJECT: dict[str, str] = {
    "Discriminator Object": "Schema Object",
    "XML Object": "Schema Object",
}

# The spec often shows an example wrapped in the key it lives under in its
# parent (``servers: [...]``, ``"components": {...}``). Unwrapping maps that
# key to the object it holds: "one" holds a single object, "many" holds a list
# or a name map of them (``parameters`` is a list in an operation, a map in
# components).
Container = typing.Literal["one", "many"]
CONTAINER_KEYS: dict[str, tuple[str, Container]] = {
    "info": ("Info Object", "one"),
    "servers": ("Server Object", "many"),
    "components": ("Components Object", "one"),
    "paths": ("Paths Object", "one"),
    "tags": ("Tag Object", "many"),
    "security": ("Security Requirement Object", "many"),
    "externalDocs": ("External Documentation Object", "one"),
    "parameters": ("Parameter Object", "many"),
    "requestBody": ("Request Body Object", "one"),
    "responses": ("Responses Object", "one"),
    "callbacks": ("Callback Object", "many"),
    "content": ("Media Type Object", "many"),
    "headers": ("Header Object", "many"),
    "links": ("Link Object", "many"),
    "examples": ("Example Object", "many"),
    "schemas": ("Schema Object", "many"),
    "securitySchemes": ("Security Scheme Object", "many"),
}

# How to build each object from an example fragment. Objects missing here have
# no way to be parsed on their own yet.
BUILDERS: dict[str, typing.Callable[[typing.Any], object]] = {
    "Info Object": cicerone.Info.from_dict,
    "Contact Object": cicerone.Contact.from_dict,
    "License Object": cicerone.License.from_dict,
    "Server Object": cicerone.Server.from_dict,
    "Server Variable Object": cicerone.ServerVariable.from_dict,
    "Components Object": lambda data: cicerone.Components.from_spec({"components": data}),
    "Paths Object": cicerone.Paths.from_dict,
    "Path Item Object": lambda data: cicerone.PathItem.from_dict("/example", data),
    "Operation Object": lambda data: cicerone.Operation.from_dict("GET", "/example", data),
    "External Documentation Object": cicerone.ExternalDocumentation.from_dict,
    "Parameter Object": cicerone.Parameter.from_dict,
    "Request Body Object": cicerone.RequestBody.from_dict,
    "Media Type Object": cicerone.MediaType.from_dict,
    "Encoding Object": cicerone.Encoding.from_dict,
    "Responses Object": lambda data: {status: cicerone.Response.from_dict(body) for status, body in data.items()},
    "Response Object": cicerone.Response.from_dict,
    "Callback Object": cicerone.Callback.from_dict,
    "Example Object": cicerone.Example.from_dict,
    "Link Object": cicerone.Link.from_dict,
    "Header Object": cicerone.Header.from_dict,
    "Tag Object": cicerone.Tag.from_dict,
    "Reference Object": cicerone.Reference.from_dict,
    "Schema Object": cicerone.Schema.from_dict,
    "Discriminator Object": cicerone.Discriminator.from_dict,
    "Security Scheme Object": cicerone.SecurityScheme.from_dict,
    "OAuth Flows Object": cicerone.OAuthFlows.from_dict,
    "OAuth Flow Object": cicerone.OAuthFlow.from_dict,
    "Security Requirement Object": _SECURITY_REQUIREMENT.validate_python,
}
