# Parser API

The parser module provides functions for loading OpenAPI specifications from various sources. 

All parsing functions return an `OpenAPISpec` object that you can use to explore and traverse the schema.

## Overview

Cicerone supports loading OpenAPI specifications from:

- **Files** (YAML or JSON, auto-detected)
- **URLs** (with content-type detection)
- **Dictionaries** (Python dict objects)
- **JSON strings**
- **YAML strings**

All parser functions are available in the `cicerone.parse` module:

```python
from cicerone import parse as cicerone_parse
```

## Parsing Functions

### `parse_spec_from_file(path)`

Load an OpenAPI specification from a file. The format (JSON or YAML) is auto-detected based on the file extension.

**Parameters:**

- `path` (str | pathlib.Path): Path to the OpenAPI specification file

**Returns:**

- `OpenAPISpec`: Parsed specification object

**Format Detection:**

- Files with `.yaml` or `.yml` extension are parsed as YAML
- Other files are tried as JSON first, with YAML as fallback

**Example:**

```python
from cicerone import parse as cicerone_parse

# Load from YAML file
spec = cicerone_parse.parse_spec_from_file("openapi.yaml")

# Load from JSON file
spec = cicerone_parse.parse_spec_from_file("openapi.json")

# Works with pathlib.Path too
from pathlib import Path
spec = cicerone_parse.parse_spec_from_file(Path("specs/api.yaml"))
```

### `parse_spec_from_url(url)`

Load an OpenAPI specification from a URL. The format is detected from the Content-Type header.

**Parameters:**

- `url` (str): URL to fetch the OpenAPI specification from

**Returns:**

- `OpenAPISpec`: Parsed specification object

**Format Detection:**

- URLs returning `application/yaml` or similar are parsed as YAML
- Other content types are tried as JSON first, with YAML as fallback

**Example:**

```python
from cicerone import parse as cicerone_parse

# Load from URL
spec = cicerone_parse.parse_spec_from_url("https://api.example.com/openapi.json")

# Works with YAML URLs too
spec = cicerone_parse.parse_spec_from_url("https://raw.githubusercontent.com/example/api/openapi.yaml")
```

### `parse_spec_from_dict(data)`

Create an OpenAPI specification from a Python dictionary.

**Parameters:**

- `data` (Mapping[str, Any]): The OpenAPI specification as a dictionary

**Returns:**

- `OpenAPISpec`: Parsed specification object

**Example:**

```python
from cicerone import parse as cicerone_parse

# From a dictionary
spec_data = {
    "openapi": "3.0.0",
    "info": {
        "title": "My API",
        "version": "1.0.0"
    },
    "paths": {
        "/users": {
            "get": {
                "summary": "List users",
                "operationId": "listUsers",
                "responses": {
                    "200": {
                        "description": "Success"
                    }
                }
            }
        }
    }
}

spec = cicerone_parse.parse_spec_from_dict(spec_data)
print(spec.info.title)  # "My API"
```

### `parse_spec_from_json(text)`

Parse an OpenAPI specification from a JSON string.

**Parameters:**

- `text` (str): JSON string containing the OpenAPI specification

**Returns:**

- `OpenAPISpec`: Parsed specification object

**Example:**

```python
from cicerone import parse as cicerone_parse

json_str = '''
{
    "openapi": "3.0.0",
    "info": {
        "title": "My API",
        "version": "1.0.0"
    },
    "paths": {}
}
'''

spec = cicerone_parse.parse_spec_from_json(json_str)
```

### `parse_spec_from_yaml(text)`

Parse an OpenAPI specification from a YAML string.

**Parameters:**

- `text` (str): YAML string containing the OpenAPI specification

**Returns:**

- `OpenAPISpec`: Parsed specification object

**Example:**

```python
from cicerone import parse as cicerone_parse

yaml_str = '''
openapi: "3.0.0"
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      operationId: listUsers
'''

spec = cicerone_parse.parse_spec_from_yaml(yaml_str)
```

## Working with Parsed Specs

Once you've parsed a specification, you can explore it using the `OpenAPISpec` object.

See [models](/models) for more information.

## Error Handling

All parser functions may raise exceptions for invalid input:

```python
from cicerone import parse as cicerone_parse
import json

try:
    spec = cicerone_parse.parse_spec_from_file("invalid.yaml")
except FileNotFoundError:
    print("File not found")
except yaml.YAMLError as e:
    print(f"Invalid YAML: {e}")
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

## OpenAPI Version Support

Cicerone supports OpenAPI 3.0.x and 3.1.x specifications:

- **OpenAPI 3.0.x**: Full support for all features
- **OpenAPI 3.1.x**: Full support including webhooks and JSON Schema extensions

The parser automatically detects the OpenAPI version from the `openapi` field in the specification.

## Performance Considerations

The parser is designed for performance. Even for large specifications (1000+ paths), parsing typically takes less than 100ms.

## See Also

- [Working with References](references.md) - Resolving $ref references
- [Spec Models](models.md) - Understanding the OpenAPI object models
