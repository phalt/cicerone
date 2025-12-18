"""OpenAPI specification models and utilities."""

from cicerone.spec.components import Components
from cicerone.spec.info import Contact, Info, License
from cicerone.spec.openapi_spec import OpenAPISpec
from cicerone.spec.operation import Operation
from cicerone.spec.path_item import PathItem
from cicerone.spec.paths import Paths
from cicerone.spec.schema import Schema
from cicerone.spec.server import Server, ServerVariable
from cicerone.spec.tag import ExternalDocumentation, Tag
from cicerone.spec.version import Version
from cicerone.spec.webhooks import Webhooks

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

# Rebuild models with forward references after all imports are resolved
from cicerone.spec.header import Header
from cicerone.spec.parameter import Parameter
from cicerone.spec.response import Response

Header.model_rebuild()
Parameter.model_rebuild()
Response.model_rebuild()
Components.model_rebuild()
