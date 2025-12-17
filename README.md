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

```python
from cicerone.spec import OpenAPISpec

# Load from a file (auto-detects YAML/JSON)
spec = OpenAPISpec.from_file("openapi.yaml")

# Or from a URL
spec = OpenAPISpec.from_url("https://api.example.com/openapi.json")

# Or from a dict/JSON/YAML string
spec = OpenAPISpec.from_dict({"openapi": "3.0.0", ...})
spec = OpenAPISpec.from_json('{"openapi": "3.0.0", ...}')
spec = OpenAPISpec.from_yaml('openapi: "3.0.0"\n...')

# Traverse operations
for operation in spec.all_operations():
    print(f"{operation.method} {operation.path} - {operation.operation_id}")

# Find specific operations
list_users = spec.operation_by_operation_id("listUsers")
if list_users:
    print(f"Found: {list_users.summary}")

# Access schemas/components
user_schema = spec.components.get("User")
if user_schema:
    print(f"User properties: {list(user_schema.properties.keys())}")
    print(f"Required fields: {user_schema.required}")

# Access raw spec data
print(f"API Version: {spec.version}")
print(f"Title: {spec.raw['info']['title']}")
```

## Features

- **Pydantic-based models**: Type-safe, validated object models
- **Multiple input formats**: Load from files, URLs, or in-memory data
- **OpenAPI 3.x and Swagger 2.0 support**: Works with both modern and legacy specs
- **Pythonic traversal**: Navigate specs using familiar Python patterns
- **Simple API**: Intuitive methods for common operations
