# 📜 Cicerone

## Explore OpenAPI schemas, the Pythonic way

[![Package version](https://img.shields.io/pypi/v/cicerone?color=%2334D058&label=latest%20version)](https://pypi.org/project/cicerone)
[![codecov](https://codecov.io/github/phalt/cicerone/graph/badge.svg?token=BAQE27Z4Y7)](https://codecov.io/github/phalt/cicerone)
![PyPI - License](https://img.shields.io/pypi/l/cicerone)

Cicerone lets you parse OpenAPI schemas into Python objects for inspection, traversal, and tooling.

The goal of Cicerone is to be fast, minimal, fully typed, and designed for Python developers by Python developers.

## Features

- **Full support**: Tested against real-world and example specifications to be 100% compliant.
- **Pydantic-based models**: Type-safe object models.
- **Multiple input formats**: Load from files, URLs, or in-memory data
- **OpenAPI 3.x support**: Works with OpenAPI 3.0 and 3.1 specifications
- **Minimal dependencies**: Only relies on Pydantic and yaml. The rest is core Python.
- **Simple API**: Intuitive methods for common operations
- **Modern Python**: Fully typed and 100% test coverage codebase.

## Installation

### pip

```sh
pip install cicerone
```

### uv

```sh
uv add cicerone
```

## Quick Start

### Parsing Specifications

Load OpenAPI specifications from various sources:

```python
from cicerone import parse as cicerone_parse

# From a file (auto-detects YAML/JSON)
file_spec = cicerone_parse.parse_spec_from_file("openapi.yaml")

# From a URL
url_spec = cicerone_parse.parse_spec_from_url("https://api.example.com/openapi.json")

# From a dictionary
dict_spec = cicerone_parse.parse_spec_from_dict({"openapi": "3.0.0", ...})

# From JSON string
json_spec = cicerone_parse.parse_spec_from_json('{"openapi": "3.0.0", ...}')

# From YAML string
yaml_spec = cicerone_parse.parse_spec_from_yaml('openapi: "3.0.0"\n...')
```

### Exploring the schema

Once parsed, traverse the schema:

```python
from cicerone import parse as cicerone_parse

spec = cicerone_parse.parse_spec_from_file('tests/fixtures/petstore_openapi3.yaml')

print("OpenAPISpec:", spec)
print("Paths:", spec.paths)
print("PathItem:", spec.paths["/users"])
print("Operation:", spec.operation_by_operation_id("listUsers"))
print("Components:", spec.components)
print("Schema:", spec.components.get_schema("User"))
user = spec.components.get_schema("User")
print(f"User properties: {list(user.properties.keys())}")

>>> OpenAPISpec: <OpenAPISpec: 'Test API' v3.0.0, 2 paths, 2 schemas>
>>> Paths: <Paths: 2 paths, 3 operations [/users, /users/{userId}]>
>>> PathItem: <PathItem: /users [GET, POST]>
>>> Operation: <Operation: GET /users, id=listUsers, 'List all users', tags=['users']>
>>> Components: <Components: 2 schemas [User, Error]>
>>> Schema: <Schema: type=object, 5 properties, required=['id', 'username', 'email']>
>>> User properties: ['id', 'username', 'email', 'age', 'roles']
```



### Resolving References

Resolve `$ref` references to their typed objects:

```python
from cicerone import parse as cicerone_parse

spec = cicerone_parse.parse_spec_from_file('tests/fixtures/petstore_openapi3.yaml')

# Resolve a reference to get a typed Schema object
# Note: pass follow_nested=True to recursively resolve all nested $refs
user_schema = spec.resolve_reference('#/components/schemas/User', follow_nested=True)
print(f"User schema type: {user_schema.type}")
print(f"Required fields: {user_schema.required}")

>>> User schema type: object
>>> Required fields: ['id', 'username', 'email']
```

### Accessing Raw Data

Access the original specification dictionary when needed:

```python
# Version information
print(f"API Version: {spec.version}")
print(f"Major: {spec.version.major}, Minor: {spec.version.minor}")

# Raw spec data
print(f"Title: {spec.raw['info']['title']}")
```
