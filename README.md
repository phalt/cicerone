# 📜 Cicerone

## Explore OpenAPI schemas, the Pythonic way

[![Package version](https://img.shields.io/pypi/v/cicerone?color=%2334D058&label=latest%20version)](https://pypi.org/project/cicerone)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cicerone?label=python%20support)
![PyPI - Downloads](https://img.shields.io/pypi/dm/cicerone)
![PyPI - License](https://img.shields.io/pypi/l/cicerone)

Cicerone lets you parse OpenAPI/Swagger schemas into Python objects for inspection, traversal, and tooling.

The goal of Cicerone is to be fast, minimal, fully typed, and designed for Python developers by Python developers.

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

Load OpenAPI/Swagger specifications from various sources:

```python
from cicerone.parse import (
    parse_spec_from_file,
    parse_spec_from_url,
    parse_spec_from_dict,
    parse_spec_from_json,
    parse_spec_from_yaml,
)

# From a file (auto-detects YAML/JSON)
file_spec = parse_spec_from_file("openapi.yaml")

# From a URL
url_spec = parse_spec_from_url("https://api.example.com/openapi.json")

# From a dictionary
dict_spec = parse_spec_from_dict({"openapi": "3.0.0", ...})

# From JSON string
json_spec = parse_spec_from_json('{"openapi": "3.0.0", ...}')

# From YAML string
yaml_spec = parse_spec_from_yaml('openapi: "3.0.0"\n...')
```

### Exploring the schema

Once parsed, traverse the schema:

```python
from cicerone.parse import parse_spec_from_file

spec = parse_spec_from_file('tests/fixtures/petstore_openapi3.yaml')

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



### Accessing Raw Data

Access the original specification dictionary when needed:

```python
# Version information
print(f"API Version: {spec.version}")
print(f"Major: {spec.version.major}, Minor: {spec.version.minor}")

# Raw spec data
print(f"Title: {spec.raw['info']['title']}")
```

## Features

- **Pydantic-based models**: Type-safe, validated object models
- **Multiple input formats**: Load from files, URLs, or in-memory data
- **OpenAPI 3.x and Swagger 2.0 support**: Works with both modern and legacy specs
- **Pythonic traversal**: Navigate specs using familiar Python patterns
- **Simple API**: Intuitive methods for common operations
