# Spec: cicerone 0.5.0 (`cicerone-next`)

Status: approved 21 October 2026. Target release: cicerone 0.5.0, then the clientele release that drops `cicerone_compat.py`. Plan: [tasks/plan.md](../tasks/plan.md). Tasks: [tasks/todo.md](../tasks/todo.md).

Supersedes the planned `SPEC-cicerone-oas32.md` in clientele's `specs/capability-map.md`.

## Objective

Ship one breaking cicerone release that parses OpenAPI 3.0, 3.1 and 3.2 correctly, resolves local and external references, and is good enough that clientele's generator consumes typed models directly and `clientele/generators/cicerone_compat.py` is deleted.

Today it is not:

- PyPI's latest is 0.3.0 (21 December 2025). Clientele pins `cicerone==0.3.0`. `main` holds an unreleased 0.4.0 (last commit June 2026) that already promotes most fields the shim digs out of `__pydantic_extra__`.
- The shim's 3.1 normaliser runs before parsing and is lossy: `type: ["integer", "string"]` becomes `int`. Without it, clientele's `get_type` crashes on list types.
- Neither cicerone nor clientele dereferences `requestBody` or `response` `$ref`s. The 1Password fixture generates `get_audit_events(result: None, data: None)`: the body and response types are silently lost.
- `main` has spec-correctness bugs (RFC 6901 escapes, Swagger 2.0 detection, parameter override, `$ref` siblings) and no OAS 3.2 support.

Evidence: clientele's generator was run against its 26 fixture specs three ways (cicerone 0.3.0 + shim, `main` + shim, `main` + no shim) and outputs diffed, plus a probe script against `main`. Findings are listed below with the result of each check.

Goals:

1. Correct, typed models for OAS 3.0.x, 3.1.x and 3.2.x, with documented semantics where versions differ.
2. One reference system: RFC 6901 pointers, shallow typed `deref`, deep pointers, external file and URL refs, `$self` and `$id` base URIs.
3. Parse diagnostics instead of silent data loss, with a strict mode.
4. Clientele generates from typed models end to end. The shim, its tests and every `model_extra` access in clientele are deleted.

Non-goals: Swagger 2.0 parsing or conversion, OpenAPI 4 (Moonwalk), JSON Schema validation of payloads, `$dynamicRef` resolution, writing or serialising specs back out (bundling to a dict is the one exception, see References).

## Tech Stack

- Python `>=3.11`, matching clientele after 2.4.0 (cicerone is a clientele dependency, so its floor cannot be higher). Internal code uses `typing.Generic[T]` and `typing.Self`; PEP 695 syntax waits for a 3.12 floor. Docs and examples show 3.14-style code. CI matrix 3.11 to 3.15, as clientele.
- Runtime dependencies unchanged: `pydantic>=2.12`, `pyyaml`. URL fetching stays on `urllib`; no `httpx` dependency.
- Dev: uv, hatchling, ruff (add `UP`, `B`, `SIM`, `RUF`, `TC` to the current `F`, `E`, `W`, `I001`), ty, pytest, pytest-cov, pytest-benchmark, hypothesis (new, for parser fuzzing).
- Corpus: APIs.guru `openapi-directory`, the OAI spec repo's examples, clientele's fixtures.

## Commands

```
Install:         uv sync
Test:            uv run pytest
Coverage:        uv run pytest --cov=cicerone --cov-branch
Lint:            uv run ruff check . && uv run ruff format --check .
Types:           uv run ty check .
Corpus:          uv run python scripts/corpus.py [--fail-under 99.5]
Clientele smoke: uv run python scripts/clientele_smoke.py   # generate + import every fixture
```

## Findings

Thirteen verified defects on `main` and five missing capabilities block shim removal; every row below was reproduced on 21 October 2026, and each becomes a regression test.

### What the shim does, and why each half exists

| Shim part | Why it exists | State on `main` | Replacement |
| --- | --- | --- | --- |
| `normalize_openapi_31_spec` (pre-parse) | 0.3.0 rejected `type` arrays | `Schema.types`, `primary_type`, `is_nullable` parse 3.1 natively | Delete. Clientele reads `types` and emits real unions |
| `schema_to_dict` / `parameter_to_dict` / `operation_to_dict` etc. | 0.3.0 kept `$ref`, `enum`, `default`, `const`, `discriminator`, `requestBody`, `deprecated` in `__pydantic_extra__` | Promoted to typed fields; raw values mirrored into `model_extra` (deprecated) | Delete. Clientele consumes typed models |
| `path_item_to_operations_dict` re-adding path parameters | Generator wants path-level params | Already merged into `Operation.parameters`, so the shim duplicates them | Delete; rely on cicerone's merge, fixed to override correctly |
| `get_pydantic_extra` | Generic extra lookup | Unneeded once typed | Delete |

### Generator output, shim versus no shim

| Fixture | 0.3.0 + shim (today) | `main` + shim | `main`, no shim (naive `model_dump`) |
| --- | --- | --- | --- |
| Twilio (`$ref` + sibling `type`) | `status: str` for 28 query params and ~110 fields | `CallEnumStatus` (correct for 3.0) | `str` again: siblings leak through |
| 1Password (`requestBody`/`response` `$ref`) | `result: None, data: None` | `result: None`, body dropped | `result: None, data: None` |
| 3.1 fixture, `type: ["integer","string"]` | `maybe: int` (wrong) | `maybe: int` (wrong) | crash: `'list' object has no attribute 'startswith'` |
| Other 23 fixtures | identical | identical | identical |

### Defects on `main`

| # | Defect | Check | Result |
| --- | --- | --- | --- |
| 1 | Swagger 2.0 reported as `3.0.0`; `parse_spec_from_dict` defaults `openapi` to `"3.0.0"`, so clientele's version guard never fires | `{"swagger": "2.0"}` | `Version('3.0.0')` |
| 2 | RFC 6901 `~1` / `~0` not decoded | `#/paths/~1users~1{id}` | `ValueError` |
| 3 | Deep pointers typed by path prefix | `#/components/responses/R/content` | returns a `Response` |
| 4 | Path-level param not overridden by operation-level param with same `name` + `in` | `q` at both levels | both kept, path-level first |
| 5 | `x-` keys under `paths` parsed as paths | `paths: {x-meta: {...}}` | `'x-meta'` in paths |
| 6 | 3.0 `$ref` siblings not ignored | `{$ref, nullable: true}` | `is_nullable == True` |
| 7 | Lenient fallback drops values with no record | `required: true` on a schema | `required == []`, nothing reported |
| 8 | Discriminator without `propertyName` aborts the whole parse | `discriminator: {mapping: {}}` | `ValidationError` |
| 9 | Non-dict operation aborts the whole parse | `get: "oops"` | `AttributeError` |
| 10 | `components.pathItems` (3.1) dropped entirely | `components: {pathItems: {...}}` | not on the model, not in extras |
| 11 | `resolve_reference` re-parses from `raw` and inlines nested refs, returning a second object graph | resolve a request body | copy `is not` the component; inner schema name lost |
| 12 | `settings.VERSION` stale | | `0.3.0` vs pyproject `0.4.0` |
| 13 | Corpus badge never updated | `.github/compatibility.json` | `0.00%` since 24 December 2025 |

Smaller items: no `py.typed`; `import cicerone` exposes nothing; `Version` has no ordering; webhooks use a fake `webhook:<name>` path; `Parameter.content` and `Header.content` are raw dicts; `parse_spec_from_url` has no timeout; CI actions are several majors behind.

### Missing capabilities

- **Reference dereferencing for codegen**: a shallow, typed `deref` that returns the canonical component and keeps nested schema refs (so class names survive).
- **External refs**: `ReferenceResolver` raises for anything not starting with `#`.
- **OAS 3.1 Schema keywords**: `$id`, `$anchor`, `$defs`, `patternProperties`, `propertyNames`, `if`/`then`/`else`, `dependentSchemas`, `contains`, `unevaluated*`, `contentMediaType`, `contentSchema` live only in `model_extra` as raw dicts.
- **OAS 3.2**: none of it (`query`, `additionalOperations`, `itemSchema`, `$self`, ...). A `3.2.0` document parses as if it were 3.0, silently dropping the new operations.
- **Diagnostics**: no way to know what lenient parsing threw away.

## Design

The central change: every parsed object knows where it came from (document URI + JSON pointer), and the spec keeps an index from location to object. Versions, diagnostics, `$ref` typing, deep pointers and external documents all hang off that.

### Package and public API

```python
import cicerone

spec = cicerone.parse_file("openapi.yaml")            # also parse_url, parse_dict, parse_text
spec = cicerone.parse_file("openapi.yaml", strict=True, allow_remote=False)

for path, item in spec.paths:
    for op in item.operations.values():
        body = spec.deref(op.request_body)           # RequestBody | None, canonical object
        for status, resp in op.responses.items():
            resp = spec.deref(resp)
            schema = resp.content["application/json"].schema_
            if schema and schema.ref:
                key = spec.component_key(schema)     # ComponentKey(kind="schemas", name="User", document=...)

for warning in spec.diagnostics:
    print(warning.code, warning.location, warning.message)
```

- `cicerone/__init__.py` re-exports `parse_*`, `OpenAPISpec`, every model, the exceptions and `__version__` (from `importlib.metadata`). Delete `cicerone/settings.py`. Ship `py.typed`.
- New names `parse_file`, `parse_url`, `parse_dict`, `parse_text` (format sniffed). The `parse_spec_from_*` functions are removed in 0.5.0, not aliased.
- All models frozen after parse (`model_config["frozen"] = True`). The resolver no longer mutates anything.
- Exceptions in `cicerone/errors.py`: `CiceroneError` > `ParseError` (carries `diagnostics`), `UnsupportedVersionError`, `RefResolutionError` (carries the ref and location), `CircularReferenceError`, `RemoteRefDisallowedError`. Avoid shadowing the builtin `ReferenceError`.

### Parse pipeline

1. Load the root document (file, URL, dict, text) into a `Document(uri, raw)`.
2. Detect the version from the root's `openapi` key only. `swagger` key or missing `openapi` → `UnsupportedVersionError`. Majors other than 3 or minors above 2 → `UnsupportedVersionError`.
3. Build models with an explicit `ParseContext` threaded through every `from_dict(data, ctx)`: `version`, `document`, `pointer`, `diagnostics`, `strict`. A public `Model.from_dict(data)` without a context still works, defaulting to the latest dialect.
4. Each model records `location: Location(uri, pointer)` as a private attribute and registers itself in `spec._index`.
5. Walk every `ref` and load referenced external documents on demand (see References). Nothing is inlined.

### Versions

`Version` becomes a frozen dataclass with `major`, `minor`, `patch`, `raw`, ordering, and `dialect: Literal["3.0", "3.1", "3.2"]`. Version-dependent behaviour is decided once, from `dialect`, at parse time:

| Behaviour | 3.0 | 3.1 | 3.2 |
| --- | --- | --- | --- |
| Schema `$ref` siblings | ignored, diagnostic `ref-siblings-ignored` | kept (JSON Schema 2020-12) | kept |
| `nullable` keyword | honoured | honoured with diagnostic `nullable-in-3.1` | same as 3.1 |
| `exclusiveMinimum`/`Maximum` | boolean modifiers | numbers | numbers |
| Reference Object `summary`/`description` | ignored | override target's | override target's |
| `query`, `additionalOperations`, `itemSchema` etc. | diagnostic `field-not-in-dialect`, still parsed | same | typed |

`Schema` gains `effective_minimum` / `effective_maximum` / `exclusive_minimum_value` helpers that hide the 3.0 versus 3.1 encoding.

### Diagnostics and strict mode

```python
@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str                 # stable, kebab-case, documented
    severity: Literal["warning", "error"]
    message: str
    location: Location
```

- Every lenient fallback (the current `lenient_validator`, skipped malformed collection entries, non-dict operations, missing `propertyName`) appends a diagnostic instead of vanishing.
- `strict=True` raises one `ParseError` carrying all error-severity diagnostics after the full walk, never on the first one.
- Lenient mode never raises for document shape. Only root-document I/O failures and unsupported versions raise. An unresolvable ref is an error diagnostic, `ref-unresolved`; `spec.deref` on it raises `RefResolutionError`.

### References

**Typing comes from the referencing site, not the pointer.** A `$ref` inside a parameter list resolves to a `Parameter`, whatever document or pointer it lands on. This fixes deep pointers (#3), external documents that hold a bare schema, and `$defs`.

- Every referenceable model has `ref: str | None` and `is_ref: bool`: Schema, Parameter, Response, RequestBody, Header, Example, Link, Callback, SecurityScheme, PathItem, MediaType (3.2). Today Callback, Example, Link and SecurityScheme lack it.
- `spec.deref(obj: T) -> T`: follows a ref chain to the canonical object (identity with `spec.components.*`), shallow. Non-ref input returned unchanged; `None` returns `None`. 3.1+ Reference Object `summary`/`description` overrides are applied on a frozen copy.
- `spec.resolve(ref: str, *, base: Location | None = None, as_type: type[T] | None = None) -> T | Any`: any pointer, typed from `as_type` or from the index.
- `spec.component_key(obj) -> ComponentKey | None`: `(kind, name, document)` for objects that live in a components map. Codegen uses this instead of string-replacing `#/components/schemas/`.
- `spec.named_schemas() -> dict[str, Schema]`: every schema reachable from paths, webhooks and components that has a component key, local or external, with deterministic, collision-free names. Name = component name for targets in a components map, else the last pointer segment, else the file stem. Order: root document first, then documents by URI, then pointer. First claimant keeps the bare name; later ones get the document stem prefixed in PascalCase (`Pet`, `ModelsPet`), with diagnostic `schema-name-collision`. Clientele's schema loop iterates this, not `components.schemas`.
- `spec.references()` replaces `get_all_references`; `spec.is_recursive(schema)` replaces `is_circular_reference`. Old `resolve_reference(follow_nested=True)` inlining is removed.
- Pointers: RFC 6901 decoding (`~1` → `/`, `~0` → `~`) after RFC 3986 percent-decoding of the fragment. `cicerone.pointer.escape()` and `join()` helpers.

**External refs.** URI resolution follows RFC 3986 section 5.

- Base URI of a document: its `$self` (3.2) if present and resolved against the retrieval URI, else the retrieval URI. `$id` inside a 3.1+ Schema sets the base for that subtree; `$anchor` registers a plain-name fragment. `$dynamicRef` is recorded but treated as `$ref` with diagnostic `dynamic-ref-unsupported`.
- `DocumentStore` caches documents by absolute URI, loads each once, detects cycles across documents, and accepts a `fetcher: Callable[[str], bytes]` for tests.
- Security defaults: relative file refs allowed, but only beneath the root document's directory unless `allow_paths=[...]` widens it. Remote (`http`, `https`) refs are off by default and need `allow_remote=True`, even when the root came from a URL; clientele's CLI passes it for `--url`. Remote fetches get a timeout (default 10 s) and a size cap. No other schemes.
- `spec.bundle() -> dict`: one self-contained 3.x dict with external targets hoisted into `components` under their `named_schemas()` names and refs rewritten. Used for tests and for anyone needing a single file. This is the only serialisation in scope.

### OAS 3.1 model additions

- `Schema`: `id_` (`$id`), `schema_dialect` (`$schema`), `anchor`, `comment`, `defs: dict[str, Schema]`, `pattern_properties`, `property_names`, `unevaluated_properties`, `unevaluated_items`, `contains`, `min_contains`, `max_contains`, `dependent_required`, `dependent_schemas`, `if_`, `then`, `else_`, `content_encoding`, `content_media_type`, `content_schema`, `xml: XML`, `external_docs`. Subschemas parsed recursively and indexed.
- `Schema` helpers: `non_null_types`, `non_null_variants` (anyOf/oneOf members that are not `{type: null}`), keep `types`, `primary_type`, `is_nullable` (now dialect-aware), `has_default`, `has_const`.
- `Components.path_items`. `Parameter.content` and `Header.content` as `dict[str, MediaType]`; `Parameter.allow_reserved`.
- Webhooks: `PathItem.path` becomes `str | None`; webhooks keep their name in `Webhooks.items` keys. The `webhook:` prefix is removed.
- Responses keep string keys; `Responses` helpers `success()` (2XX range and literal codes) and `default`.

### OAS 3.2 model additions

Field names verified against `versions/3.2.1.md` in OAI/OpenAPI-Specification.

| Object | New fields | Notes |
| --- | --- | --- |
| OpenAPI | `$self` | Base URI for refs |
| Path Item | `query`, `additionalOperations` | `operations` gains `"query"`; additional methods keyed in their original case. `Operation.method` keeps the wire case |
| Parameter | `in: querystring` | Diagnostic if combined with `query` params in one operation, or used without `content` |
| Media Type | `itemSchema`, `prefixEncoding`, `itemEncoding`, `ref` | `is_sequential` property for `text/event-stream`, `application/jsonl`, `application/x-ndjson`, `application/json-seq`, `*+json-seq`; diagnostic if `encoding` coexists with the positional fields |
| Encoding | `encoding`, `prefixEncoding`, `itemEncoding` | Nested |
| Components | `mediaTypes` | Map of Media Type or ref |
| Response | `summary` | `description` becomes optional |
| Example | `dataValue`, `serializedValue` | |
| Discriminator | `defaultMapping` | `propertyName` stays required by spec; missing → diagnostic, discriminator set to `None` |
| Tag | `summary`, `parent`, `kind` | `spec.tag_tree()`; diagnostic on unknown parent or cycles |
| Security Scheme | `deprecated`, `oauth2MetadataUrl` | |
| OAuth Flows / Flow | `deviceAuthorization`, `deviceAuthorizationUrl` | |
| Server | `name` | |
| XML | `nodeType` | `XML` becomes a typed model for all dialects |

For `text/event-stream`, `MediaType.item_schema` describes the parsed event (`data`, `event`, `id`, `retry`). Cicerone exposes it typed; interpreting `contentMediaType`/`contentSchema` on `data` is the generator's job (clientele `sse-generator`).

### Removals in 0.5.0

- `model_extra` mirroring (`mirror_extras`, every `MIRRORED_EXTRA_KEYS`). Vendor `x-` keys stay in `model_extra`; also exposed as `extensions: dict[str, Any]` on every model.
- `parse_spec_from_*`, `resolve_reference(follow_nested=...)`, `get_all_references`, `is_circular_reference`, `Components.from_spec`, `cicerone.settings`.
- `NestedField`/`SpecModel.from_dict` without context and the hand-written `Operation`/`PathItem` parsing collapse into one context-aware builder per model.

## Clientele migration

Clientele's generator moves from dicts to cicerone models in two stages: first a behaviour-preserving port locked by golden snapshots, then deliberate output fixes, each with its own changelog line.

### Stage 0: golden snapshots (before touching anything)

- `tests/generators/snapshots/<fixture>/{client,schemas}.py` for all 26 specs in `example_openapi_specs/`, `tests/fixtures/`, `server_examples/`, plus the 3.1 fixture from this spec's experiment and a 3.2 fixture.
- A test regenerates each into `tmp_path` and diffs. `UPDATE_SNAPSHOTS=1` rewrites them. Generated code is also imported, so a snapshot that does not compile fails.

### Stage 1: typed port, identical output

| File | Change |
| --- | --- |
| `cli.py` | `_load_openapi_spec` becomes `cicerone.parse_file` / `parse_url` (gains external refs). `_prepare_spec` catches `UnsupportedVersionError` instead of comparing `spec.version`. Print `spec.diagnostics` as yellow warnings; new `--strict` flag |
| `generators/shared/utils.py` | `get_type(schema: Schema, spec: OpenAPISpec) -> str`. Branches on `schema.ref`, `has_const`, `one_of`/`any_of`, `types`, `is_nullable`, `items`. `get_func_name(op: Operation, path)`. `get_param_from_ref` / `get_schema_from_ref` become `spec.deref(...)`. `schema_ref`/`param_ref` string-replacing goes; names come from `spec.component_key` |
| `generators/shared/schemas.py` | `make_schema_class(name, schema: Schema)`, `generate_class_properties(properties: dict[str, Schema], required: list[str])`. Iterate `spec.named_schemas()` |
| `generators/api/clients.py` | Iterate `spec.paths`; operations are `Operation`; parameters come from `op.parameters` only (cicerone merged and overrode path-level ones). `ParametersResponse` unchanged |
| `generators/cicerone_compat.py`, `tests/generators/test_cicerone_compat.py` | Deleted |
| `tests/generators/api/test_nullable_fields.py` | Drop its `cicerone_compat` import; build specs via `cicerone.parse_dict` |
| `pyproject.toml` | `cicerone>=0.5,<0.6` in the `cli` extra; remove the `cicerone_compat` import-linter entry |

Inline schemas that the generator synthesises today as dicts (the `{"type": "object", "properties": {"data": ...}}` fallback in `get_response_class_names`) become `Schema(type="object", ...)` constructed directly.

### Stage 2: intentional output changes

Each is its own PR with snapshot updates reviewed line by line.

1. **Dereference request bodies and responses.** 1Password's `get_audit_events` gains typed `data` and `result`. Same for `components/headers` and `components/parameters` chains.
2. **Multi-type unions.** `type: ["integer", "string"]` → `int | str`; nullable variants via `non_null_variants`.
3. **Dialect-correct `$ref` siblings.** 3.0 keeps today's behaviour (ref wins). 3.1+ applies siblings: `{$ref: Kind, description: ...}` still `Kind`; `{$ref: Kind, nullable/type null}` becomes `Kind | None`.
4. **Operation-level parameters win** over path-level ones with the same `name` + `in` (currently path-level wins via first-seen dedup).
5. **3.2 `query` operations** generate from cicerone's full QUERY support (parsed, typed, request bodies allowed, included in `all_operations` and tag lookups). Until clientele's runtime has a query verb, the generator skips them with a warning; the runtime verb is tracked in clientele, not here.
6. **Diagnostics surfaced** in CLI output.

The SSE generator (`sse-generator` in the capability map) builds on `MediaType.item_schema` and `is_sequential` and stays a separate clientele spec.

### Done means

```
grep -rn "cicerone_compat\|model_extra\|__pydantic_extra__\|#/components/schemas/" clientele/
```

returns nothing.

## Testing Strategy

Every Findings row is a failing test before its fix lands; the corpus and clientele smoke runs are the release gate.

| Layer | Where | What |
| --- | --- | --- |
| Regression | `tests/regressions/test_findings.py` | One test per defect #1 to #13 and per shim-diff row. Written first, marked `xfail(strict=True)` until fixed |
| Unit | `tests/spec/` | Each model's 3.0 / 3.1 / 3.2 fields, parametrised by dialect; version-table behaviours |
| References | `tests/references/` | RFC 6901 vectors (the RFC's own examples); chains; cycles within and across documents; deep pointers typed by site; `$id`/`$anchor`; `$self` relative and absolute; `bundle()` round-trips through `parse_dict` to an equal model graph |
| External I/O | `tests/references/test_external.py` | Fake `fetcher`; `tmp_path` multi-file trees; path escape outside root refused; remote refused without `allow_remote`; timeout and size cap. No real network in unit tests |
| Diagnostics | `tests/test_diagnostics.py` | Each code produced at the right location; `strict=True` aggregates |
| Fuzz | `tests/test_fuzz.py` | Hypothesis-generated JSON-ish documents: lenient parse never raises anything but the documented errors |
| Conformance | `tests/fixtures/oai/` | Generated from OAI/OpenAPI-Specification `versions/*.md`, vendored at a pinned commit. Field coverage: every fixed-field table row in 3.0.4, 3.1.2 and 3.2.1 (150, 153 and 176 rows) maps to a typed model field, asserted by a test that parses the tables. Examples: all ~500 YAML/JSON blocks across 3.0.0 to 3.2.1 parse (full documents via `parse_dict`, fragments via their object's `from_dict`) with zero error diagnostics |
| Corpus | `scripts/corpus.py`, weekly CI | APIs.guru 3.x specs: parse rate, ref-resolution rate, diagnostics histogram. Fails under 99.5% parse. Badge written from the script's JSON output, not a `sed` of log text |
| Downstream | `scripts/clientele_smoke.py`, CI job | Install clientele `main` against cicerone `HEAD`, generate and import every clientele fixture |
| Performance | `tests/test_performance.py` | Existing benchmarks plus Twilio (largest fixture, ~26k lines): parse time no worse than 1.5x 0.3.0 |

Coverage never slips: total line and branch coverage for `cicerone/` must not drop below its current level, and every new or changed line and branch is covered. No chasing 100% on untouched code.

The experiment harness from this analysis (three-way generation and diff) is the seed for `clientele_smoke.py`.

## Delivery

Fourteen PRs: ten in cicerone ending in the 0.5.0 release, four in clientele. Clientele's snapshot PR (C1) can land today, in parallel with all cicerone work. 0.4.0 is never published; its changelog folds into 0.5.0. Task-level breakdown: [tasks/plan.md](../tasks/plan.md).

| PR | Repo | Scope | Depends on |
| --- | --- | --- | --- |
| 1 | cicerone | Hygiene: Python `>=3.11`, CI matrix 3.11 to 3.15, current action majors, ruff rules, `py.typed`, `__init__` exports, `__version__` via metadata, delete `settings.py`, `errors.py`. Regression tests for every Findings row as strict xfails. Add the clientele smoke script, seeded from this analysis's harness | none |
| 2 | cicerone | `Version` dataclass + dialect, version detection from root only, `UnsupportedVersionError` (#1, #12) | 1 |
| 3 | cicerone | `ParseContext`, `Location`, location index, `Diagnostic`, `strict`. Lenient paths report instead of vanish; non-dict operation and discriminator crashes fixed (#7, #8, #9). Models frozen | 2 |
| 4 | cicerone | Remove `model_extra` mirroring; add `extensions`; drop `parse_spec_from_*` for `parse_*` | 3 |
| 5 | cicerone | Structural 3.0/3.1 fixes: param override (#4), `x-` under paths (#5), `$ref` siblings by dialect (#6), `components.pathItems` (#10), typed `Parameter.content`/`Header.content`, webhooks without fake paths, `XML` model | 3 |
| 6 | cicerone | Local references: RFC 6901, site-typed resolution, `deref`, `resolve`, `component_key`, `references`, `is_recursive`; delete inlining resolver (#2, #3, #11) | 5 |
| 7 | cicerone | 3.1 Schema keywords, `$id`/`$anchor`, `$defs` indexed, Schema helpers | 6 |
| 8 | cicerone | External refs: `DocumentStore`, base URIs, `$self`, security defaults, `named_schemas`, `bundle` | 7 |
| 9 | cicerone | OAS 3.2 models (table above), `tag_tree`, `is_sequential` | 8 |
| 10 | cicerone | Corpus script and badge fix (#13), docs rewrite, CHANGELOG, release 0.5.0 | 9 |
| C1 | clientele | Golden snapshots for all fixtures (Stage 0) | none |
| C2 | clientele | Typed port against cicerone 0.5.0, shim deleted, snapshots unchanged (Stage 1) | 10, C1 |
| C3 | clientele | Stage 2 items 1 to 4, one commit each, snapshot diffs reviewed | C2 |
| C4 | clientele | Diagnostics and `--strict` in the CLI; 3.2 `query` handling | C3 |

While PRs 1 to 9 are in flight, run `clientele_smoke.py` against cicerone `HEAD` on every PR from PR 4 onwards, using a local branch of clientele with C2 in progress, so API mistakes surface before release rather than after.

## Success Criteria

- cicerone 0.5.0 on PyPI; clientele depends on `cicerone>=0.5,<0.6`.
- The clientele `grep` under Clientele migration returns nothing; `cicerone_compat.py` and its tests are gone.
- All 13 Findings regression tests pass with their `xfail` markers removed.
- Clientele snapshots: Stage 1 identical to pre-migration; Stage 2 diffs limited to the listed items. 1Password has typed bodies and responses; the 3.1 fixture has `maybe: int | str`.
- Corpus: at least 99.5% of APIs.guru 3.x specs parse in lenient mode, at least 99% of their refs resolve, and the badge shows the real figure.
- 100% OAS 3.x compatibility: all patch versions 3.0.0 to 3.0.4, 3.1.0 to 3.1.2 and 3.2.0 to 3.2.1 accepted; 100% of fixed fields typed; 100% of the spec's own examples parse with zero error diagnostics.
- Coverage no lower than at the start of this work (98% branch on 21 October 2026), with all code added by this work fully covered; ruff and ty clean.

## Boundaries

- Always: write the failing test first; keep lenient mode non-raising for document shape; record a diagnostic for anything dropped; cite the OAS section in docstrings for version-specific behaviour.
- Ask first: any new runtime dependency; changing default security posture for external refs; renaming a diagnostic code after release.
- Never: inline refs into canonical objects; mutate models after parse; fetch remote refs by default from a local root; add Swagger 2.0 conversion.

## Decision Log

| Decision | Choice |
| --- | --- |
| OAS 3.2 scope | Folded in; replaces clientele's planned `SPEC-cicerone-oas32.md` |
| OAS 3.x compatibility | 100%: every patch version 3.0.0 to 3.2.1, every fixed field typed, every spec example parses |
| Clientele depth | Typed models end to end, shim deleted |
| Release posture | Straight to 0.5.0; 0.4.0 never published, no `model_extra` mirroring |
| Backwards compatibility | None. Clientele is the only consumer; old names removed, no aliases |
| External refs | In scope, with path containment |
| Remote refs | Off by default, including for URL roots; `allow_remote=True` to opt in |
| Reference representation | `ref` field on each referenceable model, not `Model \| Reference` unions |
| Ref target typing | From the referencing site, not the pointer path |
| Ref resolution | Shallow `deref` to canonical objects; inlining removed |
| External schema names | Component name, else pointer segment, else file stem; root wins, collisions get a PascalCase document-stem prefix |
| `nullable` in 3.1+ | Honoured, with diagnostic `nullable-in-3.1` |
| QUERY method | Fully supported in cicerone; clientele runtime verb tracked separately |
| Unsupported input | Swagger 2.0 and non-3.x raise `UnsupportedVersionError` |
| Python floor | 3.11, matching clientele 2.4.0 |
| Parse API names | `parse_file`/`parse_url`/`parse_dict`/`parse_text` |
| Models | Frozen after parse |
| Release gates | 99.5% corpus parse, 99% ref resolution |

## Open Questions

All resolved 21 October 2026; see the Decision Log. The one remaining check: confirm clientele's runtime query verb is on its own roadmap before C4.
