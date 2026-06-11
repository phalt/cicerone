# Change log

## 0.4.0

### Typed first-class fields

Spec-defined fields that previously only appeared in `model_extra` are now proper typed model fields:

| Model | New typed fields |
|-------|------------------|
| `Schema` | `ref` (`$ref`), `format`, `enum`, `default`, `const`, `deprecated`, `nullable`, `read_only`, `write_only`, `example`, `examples`, `discriminator`, `additional_properties` (`Schema \| bool`), `minimum`, `maximum`, `exclusive_minimum`, `exclusive_maximum`, `multiple_of`, `min_length`, `max_length`, `pattern`, `min_items`, `max_items`, `unique_items`, `min_properties`, `max_properties` |
| `Operation` | `parameters` (`list[Parameter]`), `responses` (`dict[str, Response]`), `request_body`, `security` (`None` = inherit global), `callbacks` (`dict[str, Callback]`), `deprecated`, `servers`, `external_docs` |
| `MediaType` | `schema_` is now a typed `Schema` instead of a raw dict |
| `Parameter` | `ref`, `deprecated`, `allow_empty_value` |
| `Header` | `ref`, `deprecated` |
| `RequestBody` / `Response` | `ref` |
| `Encoding` | `headers` is now `dict[str, Header]` |
| `Link` | snake_case fields (`operation_ref`, `operation_id`, `request_body`) with camelCase aliases; typed `server` |
| `PathItem` | `ref`, `summary`, `description`, typed path-level `parameters` |

- `Schema.has_default` / `Schema.has_const` distinguish an explicit `default: null` from an absent default.
- New `Discriminator` model (`property_name`, `mapping`) wired into `Schema.discriminator`.
- All models accept construction by field name as well as alias (`populate_by_name`).

### Deprecated: model_extra mirroring

For backwards compatibility, the raw source values of all promoted keys are still mirrored into `model_extra` (e.g. `schema.model_extra["$ref"]` and `operation.model_extra["requestBody"]` keep working and return the same raw data as 0.3.0). **This mirroring is deprecated and will be removed in 0.5.0** — migrate to the typed fields.

Known behavior changes that mirroring does not cover:

- `Operation.parameters` / `Operation.responses` previously held raw dicts; they now hold typed `Parameter` / `Response` objects (`param["name"]` becomes `param.name`, `param.get("$ref")` becomes `param.ref`).
- `MediaType.schema_` previously held a raw dict; it now holds a typed `Schema`.
- `Link.operationRef` / `Link.operationId` / `Link.requestBody` field names are now snake_case; the old camelCase attribute access still works via the mirrored extras until 0.5.0.
- `schema.model_dump(by_alias=True, exclude_unset=True)` is now a near drop-in replacement for hand-rolled model-to-dict conversions.

### Native OpenAPI 3.1 nullability

- `Schema.types`: always-a-list view of the `type` keyword (handles 3.1 type arrays like `type: ["string", "null"]`).
- `Schema.primary_type`: first non-`"null"` type.
- `Schema.is_nullable`: unifies the 3.0 `nullable` keyword, 3.1 type arrays containing `"null"`, and `anyOf`/`oneOf` with a `{"type": "null"}` member. OpenAPI 3.1 specs no longer need to be normalized to 3.0 before parsing.

### Query API

- `OpenAPISpec.operations_by_tag(tag)` and `OpenAPISpec.tags_to_operations()` for tag-based operation lookup.
- `Paths` is iterable as `(path, PathItem)` pairs and supports `len()`.
- Reference resolution is cached: one shared resolver per spec plus a per-resolver result cache (repeated `resolve_reference` calls return the same object).
- Broken reference errors include a did-you-mean suggestion and the available keys at the failure point.

### Robustness

- Boolean JSON schemas (`items: true`, `additionalProperties: false`) no longer crash parsing; `additionalProperties` preserves booleans, boolean `items` are skipped.
- Malformed nested values of the wrong shape are skipped (the field keeps its default) instead of crashing the parse; raw values remain available via `model_extra` where mirrored.

### Internals

- New `model_utils.SpecModel` base class with a declarative, generic `from_dict`, removing the hand-written boilerplate from most models.

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
