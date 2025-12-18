"""OpenAPI specification models and utilities."""

from cicerone.spec import (
    callback,
    components,
    encoding,
    example,
    header,
    info,
    link,
    media_type,
    model_utils,
    oauth_flows,
    openapi_spec,
    operation,
    parameter,
    path_item,
    paths,
    request_body,
    response,
    schema,
    security_scheme,
    server,
    tag,
    version,
    webhooks,
)

__all__ = [
    "Callback",
    "Components",
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
    "model_utils",
]

# Re-export for backward compatibility
Callback = callback.Callback
Components = components.Components
Contact = info.Contact
Encoding = encoding.Encoding
Example = example.Example
ExternalDocumentation = tag.ExternalDocumentation
Header = header.Header
Info = info.Info
License = info.License
Link = link.Link
MediaType = media_type.MediaType
OAuthFlow = oauth_flows.OAuthFlow
OAuthFlows = oauth_flows.OAuthFlows
OpenAPISpec = openapi_spec.OpenAPISpec
Operation = operation.Operation
Parameter = parameter.Parameter
PathItem = path_item.PathItem
Paths = paths.Paths
RequestBody = request_body.RequestBody
Response = response.Response
Schema = schema.Schema
SecurityScheme = security_scheme.SecurityScheme
Server = server.Server
ServerVariable = server.ServerVariable
Tag = tag.Tag
Version = version.Version
Webhooks = webhooks.Webhooks

# Rebuild models with forward references after all imports are resolved
header.Header.model_rebuild()
parameter.Parameter.model_rebuild()
response.Response.model_rebuild()
components.Components.model_rebuild()
