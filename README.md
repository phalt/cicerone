# 📜 Cicerone

## Explore OpenAPI schemas, the Pythonic way

[![Package version](https://img.shields.io/pypi/v/cicerone?color=%2334D058&label=latest%20version)](https://pypi.org/project/cicerone)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cicerone?label=python%20support)
![PyPI - Downloads](https://img.shields.io/pypi/dm/cicerone)
![PyPI - License](https://img.shields.io/pypi/l/cicerone)

Cicerone lets you parse OpenAPI/Swagger schemas into rich, traversable Python objects.

## Installation

### With pip (Python)

```sh
pipx install cicerone
```

### With uv (Python)

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

### Exploring Operations

Once parsed, traverse operations in your spec:

```python
from cicerone.parse import parse_spec_from_file

spec = parse_spec_from_file("openapi.yaml")

# Iterate through all operations
for operation in spec.all_operations():
    print(f"{operation.method} {operation.path} - {operation.operation_id}")

# Find a specific operation by ID
list_users = spec.operation_by_operation_id("listUsers")
if list_users:
    print(f"Summary: {list_users.summary}")
    print(f"Tags: {list_users.tags}")
```

### Accessing Schemas

Explore data models defined in your spec:

```python
# Get a schema by name
user_schema = spec.components.get("User")

if user_schema:
    # Access properties
    print(f"Properties: {list(user_schema.properties.keys())}")
    
    # Check required fields
    print(f"Required: {user_schema.required}")
    
    # Examine nested properties
    for prop_name, prop_schema in user_schema.properties.items():
        print(f"  {prop_name}: {prop_schema.type}")
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
