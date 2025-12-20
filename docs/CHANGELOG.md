# Change log

## 0.2.0

- Added the OpenAPISpec object model for traversing OpenAPI specifications to cover 100% of the OpenAPI specification.
- Added parser functions for loading specs from files, URLs, JSON, YAML, and dictionaries
- Added support for OpenAPI 3.0.x and higher specifications.
- All OpenAPI objects represented as Pydantic-based models for type-safe schema exploration
- Added comprehensive tests for parsing real-world OpenAPI schemas from APIs.guru openapi-directory
- Added comprehensive test suite for OpenAPI example schemas covering all supported features
- **Added reference navigation API for resolving $ref references in OpenAPI specifications**
  - New `Reference` model to represent OpenAPI Reference Objects
  - New `ReferenceResolver` class for navigating and resolving references
  - `resolve_reference()` method returns typed Pydantic objects (Schema, Response, etc.) not raw dicts
  - Added `get_all_references()` method to OpenAPISpec to find all references in the specification
  - Support for local references (e.g., `#/components/schemas/User`)
  - Full support for JSON Pointer syntax in references

## 0.1.0

- Initial version
