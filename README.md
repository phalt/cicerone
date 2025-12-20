# 📜 Cicerone

## Turn OpenAPI schemas into Pydantic models

[![Package version](https://img.shields.io/pypi/v/cicerone?color=%2334D058&label=latest%20version)](https://pypi.org/project/cicerone)
[![codecov](https://codecov.io/github/phalt/cicerone/graph/badge.svg?token=BAQE27Z4Y7)](https://codecov.io/github/phalt/cicerone)
![PyPI - License](https://img.shields.io/pypi/l/cicerone)

Cicerone parses OpenAPI schemas into Pydantic models for introspection and traversal.

Cicerone is the fastest, most minimal, fully typed, pythonic library for dealing with OpenAPI schemas.

## Features

- **Full support**: Tested against hundreds of real schemas to ensure 100% compliance.
- **Pydantic-based models**: Type-safe object models.
- **Multiple input formats**: Load from files, URLs, or in-memory data in various formats.
- **OpenAPI 3.x support**: Works with OpenAPI 3.0 and 3.1 specifications
- **Minimal dependencies**: Only relies on Pydantic and pyyaml. The rest is core Python.
- **Simple API**: Intuitive methods for common operations.
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

```python
from cicerone import parse as cicerone_parse

# From a file
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

```python
from cicerone import parse as cicerone_parse

spec = cicerone_parse.parse_spec_from_file('tests/fixtures/petstore_openapi3.yaml')

print("OpenAPISpec:", spec)
>>> OpenAPISpec: <OpenAPISpec: 'Test API' v3.0.0, 2 paths, 2 schemas>

print("Paths:", spec.paths)
>>> Paths: <Paths: 2 paths, 3 operations [/users, /users/{userId}]>

print("PathItem:", spec.paths["/users"])
>>> PathItem: <PathItem: /users [GET, POST]>

print("Operation:", spec.operation_by_operation_id("listUsers"))
>>> Operation: <Operation: GET /users, id=listUsers, 'List all users', tags=['users']>

print("Components:", spec.components)
>>> Components: <Components: 2 schemas [User, Error]>

print("Schema:", spec.components.get_schema("User"))
>>> Schema: <Schema: type=object, 5 properties, required=['id', 'username', 'email']>

user = spec.components.get_schema("User")
print(f"User properties: {list(user.properties.keys())}")
>>> User properties: ['id', 'username', 'email', 'age', 'roles']
```

### Resolving References

Resolve `$ref` references to their typed objects:

```python
from cicerone import parse as cicerone_parse

spec = cicerone_parse.parse_spec_from_file('tests/fixtures/petstore_openapi3.yaml')

# Resolve a reference to get a typed Schema object
# follow_nested=True will recursively resolve all nested $refs
user_schema = spec.resolve_reference('#/components/schemas/User', follow_nested=True)
print(f"User schema type: {user_schema.type}")
>>> User schema type: object
print(f"Required fields: {user_schema.required}")
>>> Required fields: ['id', 'username', 'email']
```
