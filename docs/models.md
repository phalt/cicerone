# Spec Models

Cicerone provides Pydantic-based models for all OpenAPI 3.x specification objects. These models provide type-safe access to the OpenAPI schema and make it easy to explore and traverse specifications in a pythonic way.

## Overview

All spec models are available in the `cicerone.spec` module:

```python
from cicerone.spec import (
    Callback,
    Components,
    Contact,
    Encoding,
    Example,
    ExternalDocumentation,
    Header,
    Info,
    License,
    Link,
    MediaType,
    OAuthFlow,
    OAuthFlows,
    OpenAPISpec,
    Operation,
    Parameter,
    PathItem,
    Paths,
    RequestBody,
    Response,
    Schema,
    SecurityScheme,
    Server,
    ServerVariable,
    Tag,
    Version,
    Webhooks,
)
```

Though we recommend importing just the `spec` module to maintain sensible namespacing:

```python
from cicerone import spec as cicerone_spec

cicerone_spec.OpenAPISpec
```

## Core Models

### OpenAPISpec

The top-level model representing an entire OpenAPI specification.

**Key Attributes:**

- `version` (Version): OpenAPI version
- `info` (Info): Metadata about the API
- `paths` (Paths): Available paths and operations
- `components` (Components): Reusable component definitions
- `servers` (list[Server]): Server information
- `security` (list[dict]): Global security requirements
- `tags` (list[Tag]): Available tags for grouping operations
- `webhooks` (Webhooks): Webhook definitions (OpenAPI 3.1+)
- `external_docs` (ExternalDocumentation): External documentation
- `raw` (dict): The original specification as a dictionary

**Key Methods:**

- `operation_by_operation_id(operation_id)`: Find an operation object by its operationId
- `all_operations()`: Generator yielding all operation objects
- `resolve_reference(ref)`: Resolve a $ref reference
- `get_all_references()`: Get all references in the spec

**Example:**

```python
from cicerone import parse as cicerone_parse

spec = cicerone_parse.parse_spec_from_file('openapi.yaml')

print(spec)  
>>> <OpenAPISpec: 'My API' v3.0.0, 5 paths, 10 schemas>
print(f"API: {spec.info.title} v{spec.info.version}")
>>> API: My API v3.0.0
print(f"OpenAPI version: {spec.version}")
>>> OpenAPI version 3.1.0

# Find operation
op = spec.operation_by_operation_id("createUser")
if op:
    print(f"Operation: {op.method.upper()} {op.path}")
>>> Operation: POST /users

# Iterate all operations
for operation in spec.all_operations():
    print(f"{operation.method.upper()} {operation.path} - {operation.summary}")
```

### Info

Metadata about the API.

**Key Attributes:**

- `title` (str): API title (required)
- `version` (str): API version (required)
- `description` (str | None): API description
- `terms_of_service` (str | None): Terms of service URL
- `contact` (Contact | None): Contact information
- `license` (License | None): License information
- `summary` (str | None): Short summary (OpenAPI 3.1+)

**Example:**

```python
print(f"{spec.info.title} v{spec.info.version}")
if spec.info.description:
    print(spec.info.description)
if spec.info.contact:
    print(f"Contact: {spec.info.contact.email}")
```

### Schema

Represents a JSON Schema / OpenAPI Schema object. This is one of the most commonly used models for exploring data structures.

**Key Attributes:**

- `type` (str | None): Schema type (object, array, string, number, integer, boolean, null)
- `title` (str | None): Schema title
- `description` (str | None): Schema description
- `properties` (dict[str, Schema]): Object properties (for type=object)
- `required` (list[str]): Required property names
- `items` (Schema | None): Array item schema (for type=array)
- `all_of` (list[Schema] | None): allOf composition
- `one_of` (list[Schema] | None): oneOf composition
- `any_of` (list[Schema] | None): anyOf composition
- `not_` (Schema | None): not composition

**Note:** Schema models allow extra fields to support the full JSON Schema vocabulary (format, enum, minimum, maximum, pattern, etc.)

**Example:**

```python
# Get a schema from components
user_schema = spec.components.schemas.get("User")

print(user_schema)  # <Schema: type=object, 5 properties, required=['id', 'username']>
print(f"Type: {user_schema.type}")
print(f"Required: {user_schema.required}")

# Explore properties
for prop_name, prop_schema in user_schema.properties.items():
    print(f"  {prop_name}: {prop_schema.type}")
    if prop_name in user_schema.required:
        print(f"    (required)")

# Access additional JSON Schema fields
if hasattr(user_schema, 'format'):
    print(f"Format: {user_schema.format}")
```

### Components

Container for reusable component definitions.

**Key Attributes:**

- `schemas` (dict[str, Schema]): Reusable schemas
- `responses` (dict[str, Response]): Reusable responses
- `parameters` (dict[str, Parameter]): Reusable parameters
- `examples` (dict[str, Example]): Reusable examples
- `request_bodies` (dict[str, RequestBody]): Reusable request bodies
- `headers` (dict[str, Header]): Reusable headers
- `security_schemes` (dict[str, SecurityScheme]): Security scheme definitions
- `links` (dict[str, Link]): Reusable links
- `callbacks` (dict[str, Callback]): Reusable callbacks

**Key Methods:**

- `get_schema(schema_name)`: Get a schema by name

**Example:**

```python
# List all schemas
print(f"Schemas: {list(spec.components.schemas.keys())}")

# Get a specific schema
user = spec.components.get_schema("User")
if user:
    print(f"User properties: {list(user.properties.keys())}")

# List security schemes
for name, scheme in spec.components.security_schemes.items():
    print(f"{name}: {scheme.type}")
```

## Path and Operation Models

### Paths

Container for all API paths.

**Key Attributes:**

- `items` (dict[str, PathItem]): Mapping of path strings to PathItem objects

**Key Methods:**

- `all_operations()`: Generator yielding all operations across all paths

**Example:**

```python
print(spec.paths)  # <Paths: 5 paths, 12 operations [/users, /users/{id}, ...]>

# Iterate paths
for path_str, path_item in spec.paths.items.items():
    print(f"Path: {path_str}")
    
# Get all operations
for operation in spec.paths.all_operations():
    print(f"{operation.method.upper()} {operation.path}")
```

### PathItem

Represents a single path and its operations.

**Key Attributes:**

- `path` (str): The path string (e.g., "/users/{id}")
- `summary` (str | None): Path summary
- `description` (str | None): Path description
- `get`, `post`, `put`, `delete`, `patch`, `head`, `options`, `trace` (Operation | None): HTTP method operations
- `parameters` (list[Parameter]): Parameters applicable to all operations in this path
- `servers` (list[Server]): Server overrides for this path

**Example:**

```python
users_path = spec.paths.items["/users"]
print(users_path)  # <PathItem: /users [GET, POST]>

if users_path.get:
    print(f"GET: {users_path.get.summary}")
if users_path.post:
    print(f"POST: {users_path.post.summary}")
```

### Operation

Represents a single API operation (HTTP method on a path).

**Key Attributes:**

- `method` (str): HTTP method (get, post, put, delete, etc.)
- `path` (str): The path this operation belongs to
- `operation_id` (str | None): Unique operation identifier
- `summary` (str | None): Short summary
- `description` (str | None): Detailed description
- `tags` (list[str]): Tags for grouping
- `parameters` (list[Parameter]): Operation parameters
- `request_body` (RequestBody | None): Request body definition
- `responses` (dict[str, Response]): Response definitions by status code
- `callbacks` (dict[str, Callback]): Callback definitions
- `security` (list[dict]): Security requirements
- `deprecated` (bool): Whether the operation is deprecated

**Example:**

```python
op = spec.operation_by_operation_id("createUser")

print(op)  # <Operation: POST /users, id=createUser, 'Create a new user', tags=['users']>
print(f"Method: {op.method.upper()}")
print(f"Path: {op.path}")
print(f"Summary: {op.summary}")
print(f"Tags: {op.tags}")

# Check parameters
for param in op.parameters:
    print(f"Parameter: {param.name} ({param.in_})")

# Check request body
if op.request_body:
    print(f"Request body required: {op.request_body.required}")
    
# Check responses
for status_code, response in op.responses.items():
    print(f"Response {status_code}: {response.description}")
```

### Parameter

Represents a parameter (query, path, header, or cookie).

**Key Attributes:**

- `name` (str): Parameter name
- `in_` (str): Parameter location (query, path, header, cookie)
- `description` (str | None): Parameter description
- `required` (bool): Whether required
- `deprecated` (bool): Whether deprecated
- `schema` (Schema | None): Parameter schema
- `style` (str | None): Serialization style
- `explode` (bool | None): Explode option
- `example` (Any): Example value
- `examples` (dict[str, Example]): Multiple examples

**Example:**

```python
for param in operation.parameters:
    req_str = "required" if param.required else "optional"
    print(f"{param.name} ({param.in_}): {req_str}")
    if param.schema:
        print(f"  Type: {param.schema.type}")
```

### Response

Represents an operation response.

**Key Attributes:**

- `description` (str): Response description (required)
- `headers` (dict[str, Header]): Response headers
- `content` (dict[str, MediaType]): Response content by media type
- `links` (dict[str, Link]): Response links

**Example:**

```python
success_response = operation.responses.get("200")
if success_response:
    print(f"Description: {success_response.description}")
    
    # Check content types
    for media_type, content in success_response.content.items():
        print(f"Media type: {media_type}")
        if content.schema:
            print(f"  Schema: {content.schema.type}")
```

### RequestBody

Represents a request body definition.

**Key Attributes:**

- `description` (str | None): Request body description
- `content` (dict[str, MediaType]): Content by media type
- `required` (bool): Whether required

**Example:**

```python
if operation.request_body:
    print(f"Required: {operation.request_body.required}")
    
    for media_type, content in operation.request_body.content.items():
        print(f"Content type: {media_type}")
        if content.schema:
            print(f"  Schema: {content.schema}")
```

## Server Models

### Server

Represents a server definition.

**Key Attributes:**

- `url` (str): Server URL
- `description` (str | None): Server description
- `variables` (dict[str, ServerVariable]): Server variables for URL templating

**Example:**

```python
for server in spec.servers:
    print(f"Server: {server.url}")
    if server.description:
        print(f"  {server.description}")
    
    for var_name, var in server.variables.items():
        print(f"  Variable {var_name}: default={var.default}")
```

### ServerVariable

Represents a server URL template variable.

**Key Attributes:**

- `enum` (list[str] | None): Allowed values
- `default` (str): Default value
- `description` (str | None): Variable description

## Security Models

### SecurityScheme

Represents a security scheme definition.

**Key Attributes:**

- `type` (str): Security type (apiKey, http, oauth2, openIdConnect, mutualTLS)
- `description` (str | None): Security scheme description
- `name` (str | None): Parameter name (for apiKey)
- `in_` (str | None): Parameter location (for apiKey)
- `scheme` (str | None): HTTP authorization scheme (for http)
- `bearer_format` (str | None): Bearer token format (for http bearer)
- `flows` (OAuthFlows | None): OAuth flow definitions (for oauth2)
- `open_id_connect_url` (str | None): OpenID Connect URL (for openIdConnect)

**Example:**

```python
for name, scheme in spec.components.security_schemes.items():
    print(f"{name}: {scheme.type}")
    
    if scheme.type == "http":
        print(f"  Scheme: {scheme.scheme}")
    elif scheme.type == "apiKey":
        print(f"  In: {scheme.in_}, Name: {scheme.name}")
    elif scheme.type == "oauth2" and scheme.flows:
        if scheme.flows.authorization_code:
            print(f"  Auth URL: {scheme.flows.authorization_code.authorization_url}")
```

## Content Models

### MediaType

Represents content for a specific media type.

**Key Attributes:**

- `schema` (Schema | None): Content schema
- `example` (Any): Example value
- `examples` (dict[str, Example]): Multiple examples
- `encoding` (dict[str, Encoding]): Encoding information

**Example:**

```python
content = response.content.get("application/json")
if content and content.schema:
    print(f"Schema: {content.schema.type}")
```

### Example

Represents an example value.

**Key Attributes:**

- `summary` (str | None): Example summary
- `description` (str | None): Example description
- `value` (Any): The example value
- `external_value` (str | None): URL to external example

## Other Models

### Tag

Represents a tag for grouping operations.

**Key Attributes:**

- `name` (str): Tag name
- `description` (str | None): Tag description
- `external_docs` (ExternalDocumentation | None): External documentation

**Example:**

```python
for tag in spec.tags:
    print(f"Tag: {tag.name}")
    if tag.description:
        print(f"  {tag.description}")
```

### Callback

Represents a callback definition.

**Key Attributes:**

- `expressions` (dict[str, PathItem]): Callback expressions

**Example:**

```python
for name, callback in spec.components.callbacks.items():
    print(f"Callback: {name}")
    for expr, path_item in callback.expressions.items():
        print(f"  Expression: {expr}")
```

### Webhooks

Container for webhook definitions (OpenAPI 3.1+).

**Key Attributes:**

- `items` (dict[str, PathItem]): Webhook definitions

**Key Methods:**

- `all_operations()`: Generator yielding all webhook operations

**Example:**

```python
for webhook_name, path_item in spec.webhooks.items.items():
    print(f"Webhook: {webhook_name}")
    for operation in path_item.all_operations():
        print(f"  {operation.method.upper()}: {operation.summary}")
```

### Version

Represents an OpenAPI version.

**Key Attributes:**

- `major` (int): Major version number
- `minor` (int): Minor version number
- `patch` (int): Patch version number

**Example:**

```python
print(f"OpenAPI {spec.version.major}.{spec.version.minor}.{spec.version.patch}")

if spec.version.major == 3 and spec.version.minor >= 1:
    print("OpenAPI 3.1+ features available")
```

## Model Features

### String Representations

All models provide helpful string representations:

```python
print(spec)
# <OpenAPISpec: 'My API' v3.0.0, 5 paths, 10 schemas>

print(spec.paths)
# <Paths: 5 paths, 12 operations [/users, /users/{id}, ...]>

print(spec.components)
# <Components: 10 schemas, 5 responses, 3 parameters>

operation = spec.operation_by_operation_id("listUsers")
print(operation)
# <Operation: GET /users, id=listUsers, 'List all users', tags=['users']>
```

### Extra Fields

All models use Pydantic's `extra="allow"` configuration to preserve:

- Vendor extensions (x-* fields)
- Future OpenAPI additions

**Example:**

```python
# Access vendor extensions
if hasattr(spec.info, 'x_custom_field'):
    print(f"Custom: {spec.info.x_custom_field}")

# Access via raw dict
custom_value = spec.raw.get('x-api-id')
```

### Type Safety

All models are fully typed using Pydantic, providing:

- Runtime validation
- IDE autocomplete
- Type checking with mypy/pyright/ty

```python
from cicerone.spec import Schema

# Type hints work
schema: Schema = spec.components.schemas["User"]

# IDE knows what properties are available
print(schema.type)  # ✓ IDE autocomplete
print(schema.properties)  # ✓ IDE autocomplete
```

## See Also

- [Parser API](parser.md) - Loading specifications
- [Working with References](references.md) - Resolving $ref references
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0) - Official spec
