# Change log

## Unreleased

### Added

- **Major: Added `to_dict()` methods to all spec models** - This completes cicerone's API by providing the inverse operation to `from_dict()`. You can now convert parsed Pydantic models back to dictionary format, which is essential for:
  - Code generation with template engines
  - Serialization to JSON/YAML
  - Accessing Pydantic extra fields (`$ref`, `enum`, `format`, `nullable`, vendor extensions)
  - Integration with downstream tools that expect dict structures

  The following models now have `to_dict()` methods:
  - `Schema` - Handles nested schemas, composition keywords (allOf/oneOf/anyOf), and extra fields
  - `Parameter` - Converts parameters with proper field name mapping (`in_` → `"in"`)
  - `RequestBody` - Converts request bodies with nested media types
  - `Response` - Converts responses with content, headers, and links
  - `Operation` - Converts operations with parameters, responses, and requestBody
  - `PathItem` - Converts path items with operations and path-level parameters
  - `MediaType`, `Example`, `Header`, `Link`, `Encoding` - Support models

  **Why this matters:** The [clientele](https://github.com/phalt/clientele) project maintained a ~400 line compatibility layer (`cicerone_compat.py`) to work around this missing functionality. With native `to_dict()` methods, downstream projects can eliminate such workarounds and use cicerone's API directly.

  See `docs/CLIENTELE_COMPATIBILITY.md` for a detailed explanation of the problem and solution.

### Fixed

- Fixed `PathItem.from_dict()` to preserve path-level parameters and other non-operation fields in Pydantic extra fields, making them accessible via `to_dict()`

## 0.3.0

- Fixed path-level parameters not being merged into operation parameters.

## 0.2.0

- Added the OpenAPISpec object model. Traverse OpenAPI specifications as pydantic models - covers 100% of the OpenAPI specification.
- Added parser functions for loading specs from files, URLs, JSON, YAML, and dictionaries.
- Added support for OpenAPI 3.0.x and higher specifications.
- Added comprehensive tests for parsing real-world OpenAPI schemas.
- Added comprehensive test suite for OpenAPI example schemas.
- Added reference navigation API for resolving $ref references in OpenAPI specifications
- Full support for JSON Pointer syntax in references

## 0.1.0

- Initial version
