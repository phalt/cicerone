# Change log

## 0.2.0

- Added OpenAPISpec object model for traversing OpenAPI specifications
- Implemented parser functions for loading specs from files, URLs, JSON, YAML, and dictionaries
- Added support for OpenAPI 3.0.x and 3.1.x specifications
- Provided Pydantic-based models for type-safe schema exploration
- Added full Pydantic models for all OpenAPI component types with complete spec compliance including:
  - Schema
  - Parameter
  - Response
  - RequestBody
  - Example
  - SecurityScheme
  - Header
  - MediaType
  - Link
  - Callback
  - OAuthFlows
- Added comprehensive tests for parsing real-world OpenAPI schemas from APIs.guru openapi-directory.

## 0.1.0

- Initial version
