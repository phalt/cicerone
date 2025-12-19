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
  - Added `resolve_reference()` method to OpenAPISpec for resolving references to their target objects
  - Added `get_all_references()` method to OpenAPISpec to find all references in the specification
  - Added `is_circular_reference()` method to OpenAPISpec for detecting circular reference chains
  - Support for local references (e.g., `#/components/schemas/User`)
  - Automatic detection and prevention of infinite loops from circular references
  - Full support for JSON Pointer syntax in references
  - Comprehensive test coverage for all reference functionality

## 0.1.0

- Initial version
