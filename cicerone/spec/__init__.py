"""OpenAPI specification models and utilities."""

from cicerone.spec import components
from cicerone.spec import info
from cicerone.spec import openapi_spec
from cicerone.spec import operation
from cicerone.spec import path_item
from cicerone.spec import paths
from cicerone.spec import schema
from cicerone.spec import server
from cicerone.spec import tag
from cicerone.spec import version
from cicerone.spec import webhooks

__all__ = [
    "Components",
    "Contact",
    "ExternalDocumentation",
    "Info",
    "License",
    "OpenAPISpec",
    "Operation",
    "PathItem",
    "Paths",
    "Schema",
    "Server",
    "ServerVariable",
    "Tag",
    "Version",
    "Webhooks",
]

# Re-export for backward compatibility
Components = components.Components
Contact = info.Contact
ExternalDocumentation = tag.ExternalDocumentation
Info = info.Info
License = info.License
OpenAPISpec = openapi_spec.OpenAPISpec
Operation = operation.Operation
PathItem = path_item.PathItem
Paths = paths.Paths
Schema = schema.Schema
Server = server.Server
ServerVariable = server.ServerVariable
Tag = tag.Tag
Version = version.Version
Webhooks = webhooks.Webhooks

# Rebuild models with forward references after all imports are resolved
from cicerone.spec import header
from cicerone.spec import parameter
from cicerone.spec import response

header.Header.model_rebuild()
parameter.Parameter.model_rebuild()
response.Response.model_rebuild()
components.Components.model_rebuild()
