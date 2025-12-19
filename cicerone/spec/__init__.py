"""OpenAPI specification models and utilities."""

from cicerone.spec.callback import Callback
from cicerone.spec.components import Components
from cicerone.spec.encoding import Encoding
from cicerone.spec.example import Example
from cicerone.spec.header import Header
from cicerone.spec.info import Contact, Info, License
from cicerone.spec.link import Link
from cicerone.spec.media_type import MediaType
from cicerone.spec.oauth_flows import OAuthFlow, OAuthFlows
from cicerone.spec.openapi_spec import OpenAPISpec
from cicerone.spec.operation import Operation
from cicerone.spec.parameter import Parameter
from cicerone.spec.path_item import PathItem
from cicerone.spec.paths import Paths
from cicerone.spec.request_body import RequestBody
from cicerone.spec.response import Response
from cicerone.spec.schema import Schema
from cicerone.spec.security_scheme import SecurityScheme
from cicerone.spec.server import Server, ServerVariable
from cicerone.spec.tag import ExternalDocumentation, Tag
from cicerone.spec.version import Version
from cicerone.spec.webhooks import Webhooks

Header.model_rebuild()
Parameter.model_rebuild()
Response.model_rebuild()
Components.model_rebuild()

__all__ = [
    "Callback",
    "Components",
    "Contact",
    "Contact",
    "Encoding",
    "Example",
    "ExternalDocumentation",
    "Header",
    "Info",
    "License",
    "Link",
    "MediaType",
    "OAuthFlow",
    "OAuthFlows",
    "OpenAPISpec",
    "Operation",
    "Parameter",
    "PathItem",
    "Paths",
    "RequestBody",
    "Response",
    "Schema",
    "SecurityScheme",
    "Server",
    "ServerVariable",
    "Tag",
    "Version",
    "Webhooks",
]
