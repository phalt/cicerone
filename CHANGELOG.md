# Change log

## 0.2.0

- Added OpenAPISpec object model for traversing OpenAPI specifications
- Implemented parser functions for loading specs from files, URLs, JSON, YAML, and dictionaries
- Added support for OpenAPI 3.0.x and 3.1.x specifications
- Provided Pydantic-based models for type-safe schema exploration
- Added full Pydantic models for all OpenAPI component types with complete spec compliance including:
  - Schema (with support for allOf, oneOf, anyOf, not composition keywords)
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
- Added support for OpenAPI 3.1 webhooks feature
- Added models for top-level OpenAPI objects:
  - Info (with Contact and License)
  - Server (with ServerVariable for URL templating)
  - Tag (with ExternalDocumentation)
  - Webhooks
- Added comprehensive tests for parsing real-world OpenAPI schemas from APIs.guru openapi-directory
- Added comprehensive test suite for OpenAPI example schemas covering all supported features

## 0.1.0

- Initial version
