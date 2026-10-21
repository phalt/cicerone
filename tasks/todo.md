# Tasks: cicerone 0.5.0 (`cicerone-next`)

Plan: [tasks/plan.md](plan.md). Spec: [specs/SPEC-cicerone-next.md](../specs/SPEC-cicerone-next.md).

Standard checks for every task (referred to below as **checks**):

```
uv run ruff format --check . && uv run ruff check . && uv run ty check .
```

Every task also keeps the full suite green (`uv run pytest`) and coverage from slipping (`uv run pytest --cov=cicerone --cov-branch`): total coverage never drops, and every line and branch the task adds or changes is covered. Don't chase coverage on code the task doesn't touch. When a task fixes a Finding, it deletes that test's `xfail` marker and any `ty: ignore` on its lines in the same change (ty fails on unused suppressions). When it closes a conformance gap, it removes the entry from the Task 4 allowlist in the same change.

Finding numbers (#1 to #13) refer to the Defects table in the spec.

---

## Phase 1: Foundation (spec PR 1)

## Task 1: Tooling floor

**Description:** Raise `requires-python` to `>=3.11`, extend the ruff rule set with `UP`, `B`, `SIM`, `RUF`, `TC` and fix the fallout, update `ci.yml` to a 3.11 to 3.15 matrix with current major versions of `actions/checkout`, `actions/setup-python` and `astral-sh/setup-uv`, add `cicerone/py.typed`, and add `hypothesis` to the dev group. No behaviour change.

**Acceptance criteria:**
- [x] `pyproject.toml` says `>=3.11`; CI runs 3.11, 3.12, 3.13, 3.14, 3.15
- [x] New ruff rules enabled with no per-file ignores beyond the existing pattern
- [x] `py.typed` ships in the wheel (`uv build` then inspect)

**Verification:**
- [x] Tests pass: `uv run pytest`
- [x] Checks pass
- [x] Manual check: `unzip -l dist/*.whl | grep py.typed`

**Dependencies:** None

**Files likely touched:**
- `pyproject.toml`, `uv.lock`
- `.github/workflows/ci.yml`
- `cicerone/py.typed`
- Mechanical ruff fixes across `cicerone/` (auto-fix only; review the diff)

**Estimated scope:** Small (mechanical fixes may touch many files but carry no logic)

## Task 2: Package surface and exception hierarchy

**Description:** Make `import cicerone` useful: re-export the parse functions, `OpenAPISpec`, every model and the exceptions, and expose `__version__` via `importlib.metadata`. Delete `cicerone/settings.py` (Finding #12). Add `cicerone/errors.py` with `CiceroneError`, `ParseError` (carries `diagnostics`), `UnsupportedVersionError`, `RefResolutionError`, `CircularReferenceError`, `RemoteRefDisallowedError`. Nothing raises them yet except where noted in later tasks.

**Acceptance criteria:**
- [x] `cicerone.__version__` equals the installed distribution version
- [x] `cicerone.__all__` lists the public API; `from cicerone import *` works and imports nothing private
- [x] No module named `cicerone.settings`

**Verification:**
- [x] Tests pass: `uv run pytest tests/test_package.py -vv`
- [x] Checks pass

**Dependencies:** 1

**Files likely touched:**
- `cicerone/__init__.py`
- `cicerone/errors.py`
- `cicerone/settings.py` (deleted)
- `tests/test_package.py`, `tests/test_version.py`

**Estimated scope:** Small

## Task 3: Regression tests for every Finding

**Description:** Add `tests/regressions/test_findings.py` with one test per Finding #1 to #11 and #13's measurable part (the badge JSON is produced from data, checked in Task 32), plus the three shim-diff rows: Twilio `$ref` + sibling `type` under 3.0, 1Password request body / response deref, 3.1 multi-type `type` array. Each asserts the spec's intended behaviour and is marked `xfail(strict=True, reason="Finding #N")`. Fixtures are minimal inline dicts, not the large realworld files.

**Acceptance criteria:**
- [x] One clearly named test per Finding, each xfailing for the reason recorded in the spec
- [x] Tests assert the target behaviour from the spec, not today's behaviour
- [x] Shim-diff rows assert on cicerone APIs only (no clientele import)

**Verification:**
- [x] Tests pass (as xfails): `uv run pytest tests/regressions -vv`
- [x] Checks pass
- [x] Manual check: temporarily drop one marker and confirm the test fails for the stated reason

**Dependencies:** 2

**Files likely touched:**
- `tests/regressions/__init__.py`
- `tests/regressions/test_findings.py`

**Estimated scope:** Small

## Task 4: OAI conformance ratchet

**Description:** Vendor `versions/3.0.0.md` to `versions/3.2.1.md` (non-editors files) from OAI/OpenAPI-Specification at a pinned commit into `tests/fixtures/oai/`, with the commit recorded in a `SOURCE` file and a refresh script. Add two tests. Field coverage: parse the `| <a name=...>` fixed-field tables from 3.0.4, 3.1.2 and 3.2.1 (150, 153, 176 rows) and assert each (object, field) maps to a typed model field, via an explicit mapping table. Examples: extract every ```yaml and ```json block from every patch version, classify it as a full document (has `openapi`) or a fragment of the object named by its section heading, and parse it with zero error diagnostics. Both tests read an allowlist (`tests/fixtures/oai/allowlist.toml`) of known gaps with a reason per entry; anything not allowlisted must pass, and an allowlisted entry that now passes fails the test (forcing its removal).

**Acceptance criteria:**
- [ ] Pinned vendored copy plus `scripts/refresh_oai.py`; tests do not touch the network
- [ ] Field-coverage test enumerates all 479 table rows; today's gaps are allowlisted with reasons
- [ ] Example test classifies every block; non-document blocks with no object mapping are listed with a reason, not silently skipped

**Verification:**
- [ ] Tests pass: `uv run pytest tests/conformance -vv`
- [ ] Checks pass
- [ ] Manual check: print allowlist sizes and record them in the PR description as the starting ratchet

**Dependencies:** 2

**Files likely touched:**
- `tests/fixtures/oai/` (vendored markdown, `SOURCE`, `allowlist.toml`)
- `scripts/refresh_oai.py`
- `tests/conformance/test_field_coverage.py`
- `tests/conformance/test_spec_examples.py`
- `tests/conformance/oai_tables.py` (table and example extraction helpers)

**Estimated scope:** Medium

## Task 5: Clientele smoke script

**Description:** Turn the analysis harness into `scripts/clientele_smoke.py`: given a clientele checkout (path argument, default `../clientele`), generate a client for every fixture under its `example_openapi_specs/`, `tests/fixtures/` and `server_examples/` using the cicerone in the current environment, import each generated package, and optionally diff against a saved baseline directory. Exit non-zero on crash or import failure. Add a CI job that runs it against clientele `main`, marked `continue-on-error: true` until Task 36.

**Acceptance criteria:**
- [ ] Runs end to end against clientele `main` with today's cicerone and reports 26 fixtures, 1 empty-file skip
- [ ] `--baseline DIR` and `--write-baseline DIR` produce and compare outputs
- [ ] CI job present and non-blocking

**Verification:**
- [ ] Manual check: `uv run python scripts/clientele_smoke.py ../clientele` succeeds locally
- [ ] Checks pass

**Dependencies:** 2

**Files likely touched:**
- `scripts/clientele_smoke.py`
- `.github/workflows/ci.yml`

**Estimated scope:** Small

## Checkpoint 1: Foundation
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Regression xfails and conformance allowlists recorded as the baseline
- [ ] Smoke script runs against clientele `main`
- [ ] Review with human before proceeding

---

## Phase 2: Versions and parse context (spec PRs 2, 3)

## Task 6: Version and dialect

**Description:** Replace `cicerone/spec/version.py` with a frozen, ordered dataclass (`major`, `minor`, `patch`, `raw`, `dialect: Literal["3.0", "3.1", "3.2"]`). Version detection reads the root's `openapi` key only. A `swagger` key, a missing `openapi`, a major other than 3 or a minor above 2 raises `UnsupportedVersionError`. Remove the `arbitrary_types_allowed` workaround on `OpenAPISpec`. Fixes #1.

**Acceptance criteria:**
- [ ] Every patch version 3.0.0 to 3.2.1 parses and reports the right dialect
- [ ] Swagger 2.0, `4.0.0`, `3.3.0` and a missing `openapi` key raise `UnsupportedVersionError`
- [ ] `Version` supports `<`, `==`, hashing; `str(v) == v.raw`

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_version.py tests/regressions -vv`
- [ ] Checks pass
- [ ] Finding #1 xfail removed

**Dependencies:** 3

**Files likely touched:**
- `cicerone/spec/version.py`
- `cicerone/parse/parser.py`
- `cicerone/spec/openapi_spec.py`
- `tests/spec/test_version.py`, `tests/regressions/test_findings.py`

**Estimated scope:** Small

## Task 7: ParseContext, Location, Diagnostic; Schema on the builder

**Description:** Add `cicerone/context.py` with `Location(uri, pointer)`, `Diagnostic(code, severity, message, location)` and `ParseContext(version, document_uri, pointer, diagnostics, strict)` with a `child(segment)` helper that escapes per RFC 6901. Extend `SpecModel.from_dict(data, ctx=None)` so models record `_location` and register in a per-parse index. Migrate `Schema` to it, including all nested schemas, and turn `lenient_validator` fallbacks into `invalid-value` diagnostics at the right location. `OpenAPISpec` gains `diagnostics` and a private `_index`. Partly fixes #7 (Schema only).

**Acceptance criteria:**
- [ ] Every Schema in a parsed spec has a correct `Location`, including inside `properties`, `items`, `allOf` and so on
- [ ] Malformed Schema scalars produce one diagnostic each with code, location and the raw value in the message
- [ ] Parsing without a context (`Schema.from_dict(d)`) still works and defaults to the latest dialect

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_schema*.py tests/test_diagnostics.py -vv`
- [ ] Checks pass
- [ ] Manual check: parse Twilio and confirm the index size equals the number of Schema objects created

**Dependencies:** 6

**Files likely touched:**
- `cicerone/context.py`
- `cicerone/spec/model_utils.py`
- `cicerone/spec/schema.py`
- `cicerone/spec/openapi_spec.py`
- `tests/test_diagnostics.py`

**Estimated scope:** Medium

## Task 8: Builder group A: operations and paths

**Description:** Move `Operation`, `PathItem`, `Paths`, `Webhooks` and `Callback` onto the context-aware builder, collapsing their hand-written `from_dict` bodies. A non-dict operation, path item or callback becomes a `malformed-object` diagnostic instead of a crash. Path-level parameter merging keeps today's ordering for now (Task 13 changes it). Fixes #9.

**Acceptance criteria:**
- [ ] `get: "oops"` parses with one diagnostic at `#/paths/~1a/get`
- [ ] Locations recorded for every Operation, PathItem and Callback, with RFC 6901-escaped path keys
- [ ] Callback and PathItem import cycle handled without `model_rebuild(raise_errors=False)` hacks where possible

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_operation.py tests/spec/test_path_item.py tests/spec/test_paths.py tests/spec/test_webhooks.py tests/spec/test_callback.py tests/regressions -vv`
- [ ] Checks pass
- [ ] Finding #9 xfail removed

**Dependencies:** 7

**Files likely touched:**
- `cicerone/spec/operation.py`
- `cicerone/spec/path_item.py`
- `cicerone/spec/paths.py`
- `cicerone/spec/webhooks.py`
- `cicerone/spec/callback.py`

**Estimated scope:** Medium

## Task 9: Builder group B: request and response

**Description:** Move `Parameter`, `Header`, `MediaType`, `Encoding`, `Example`, `Response`, `RequestBody`, `Link` and `Discriminator` onto the builder. Each file's change is small and mechanical (declare nested fields, drop custom parsing). A discriminator without `propertyName` becomes a `missing-required-field` diagnostic and `Schema.discriminator = None` instead of aborting the parse. Fixes #8.

**Acceptance criteria:**
- [ ] `discriminator: {mapping: {}}` parses with one diagnostic and `discriminator is None`
- [ ] Locations recorded for all nine model types
- [ ] No behaviour change in existing tests other than #8

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec -vv`
- [ ] Checks pass
- [ ] Finding #8 xfail removed

**Dependencies:** 7

**Files likely touched:**
- `cicerone/spec/parameter.py`, `header.py`, `media_type.py`, `encoding.py`, `example.py`
- `cicerone/spec/response.py`, `request_body.py`, `link.py`, `discriminator.py`

**Estimated scope:** Medium (nine small files, one pattern applied repeatedly; split into two commits if review is easier)

## Task 10: Builder group C, strict mode, freeze

**Description:** Move `Components`, `Info`, `Server`, `Tag`, `SecurityScheme` and `OAuthFlows` onto the builder; `Components.from_spec` is replaced by a normal nested field. Every remaining lenient path now emits a diagnostic (completes #7). Add `strict=True` to the parse functions: collect all error-severity diagnostics over the full walk, then raise one `ParseError`. Set `frozen=True` on the models the old `ReferenceResolver` can never reach (`OpenAPISpec`, `Info`, `Contact`, `License`, `Server`, `ServerVariable`, `Tag`, `ExternalDocumentation`, `Paths`, `Webhooks`). Its `__dict__` writes can touch any model nested under a resolved component, so everything else freezes in Task 19 when that resolver is deleted.

**Acceptance criteria:**
- [ ] Finding #7 passes for every model type, not just Schema
- [ ] `strict=True` on a document with three bad values raises once with three diagnostics
- [ ] Assigning to a field of a frozen model raises

**Verification:**
- [ ] Tests pass: `uv run pytest -vv`
- [ ] Checks pass
- [ ] Finding #7 xfail removed

**Dependencies:** 8, 9

**Files likely touched:**
- `cicerone/spec/components.py`, `info.py`, `server.py`, `tag.py`, `security_scheme.py`, `oauth_flows.py`
- `cicerone/parse/parser.py`
- `tests/test_diagnostics.py`

**Estimated scope:** Medium

## Checkpoint 2: Parse context
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Every model built through `ParseContext`; no hand-written `from_dict` bodies remain outside `model_utils.py`
- [ ] Realworld fixtures parse with diagnostics counts recorded in the PR
- [ ] Review with human before proceeding

---

## Phase 3: API cleanup (spec PR 4)

## Task 11: Remove `model_extra` mirroring

**Description:** Delete `mirror_extras` and every `MIRRORED_EXTRA_KEYS`. Add an `extensions: dict[str, Any]` property on the base model returning the `x-` keys from `model_extra`. Rewrite tests that read mirrored extras to use typed fields.

**Acceptance criteria:**
- [ ] `grep -rn "MIRRORED_EXTRA_KEYS\|mirror_extras" cicerone/` returns nothing
- [ ] `model_extra` holds only keys that are not spec fields
- [ ] `extensions` returns exactly the `x-` keys

**Verification:**
- [ ] Tests pass: `uv run pytest -vv`
- [ ] Checks pass

**Dependencies:** 10

**Files likely touched:**
- `cicerone/spec/model_utils.py`
- `cicerone/spec/schema.py`, `operation.py`, `parameter.py`, `header.py`, `response.py`, `request_body.py`
- `tests/spec/test_typed_fields.py`

**Estimated scope:** Medium

## Task 12: `parse_*` API

**Description:** Replace `parse_spec_from_dict/json/yaml/file/url` with `parse_dict`, `parse_text` (sniffs JSON then YAML), `parse_file` (extension hint, then sniff) and `parse_url` (timeout parameter, default 10 s; Content-Type hint, then sniff). All take `strict` and, as no-ops until Tasks 22 and 23, `allow_paths` and `allow_remote`. Update tests and README examples that call the old names.

**Acceptance criteria:**
- [ ] Old names are gone; new names exported from `cicerone`
- [ ] `parse_url` honours a timeout (tested against a local `http.server` that stalls)
- [ ] YAML with a `.json` extension and JSON with a `.yaml` extension both parse

**Verification:**
- [ ] Tests pass: `uv run pytest tests/parse -vv`
- [ ] Checks pass

**Dependencies:** 11

**Files likely touched:**
- `cicerone/parse/parser.py`, `cicerone/parse/__init__.py`, `cicerone/__init__.py`
- `tests/parse/test_parser.py`
- `README.md`

**Estimated scope:** Small

## Checkpoint 3: Public API shape
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Start a clientele branch for C2 against cicerone `main`; run `clientele_smoke.py` and record what breaks
- [ ] Review with human before proceeding

---

## Phase 4: Structural fixes (spec PR 5)

## Task 13: Parameter override and `x-` keys under `paths`

**Description:** When merging path-level parameters into an operation, an operation-level parameter with the same `(name, in)` replaces the path-level one, keeping operation order. Matching uses resolved names, so a `$ref` parameter is matched after Task 17; until then, unresolved refs never match and a `TODO(Task 17)` test pins that. `x-` keys under `paths` are extensions, not paths. Fixes #4, #5.

**Acceptance criteria:**
- [ ] `q` at both levels yields one parameter, the operation's
- [ ] `paths: {x-meta: {...}}` produces no path and `paths.extensions == {"x-meta": ...}`
- [ ] `PathItem.parameters` still holds the path-level list unmerged

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_path_item.py tests/spec/test_paths.py tests/regressions -vv`
- [ ] Checks pass
- [ ] Findings #4 and #5 xfails removed

**Dependencies:** 10

**Files likely touched:**
- `cicerone/spec/path_item.py`
- `cicerone/spec/paths.py`
- `tests/spec/test_path_item.py`, `tests/spec/test_paths.py`

**Estimated scope:** Small

## Task 14: Dialect semantics for Schema

**Description:** Apply the spec's version table to `Schema`. In 3.0, siblings of `$ref` are dropped at parse time with one `ref-siblings-ignored` diagnostic; in 3.1+ they are kept. `nullable` is honoured in every dialect, with a `nullable-in-3.1` warning in 3.1+. `is_nullable` becomes dialect-aware. Add `effective_minimum`, `effective_maximum`, `exclusive_minimum_value`, `exclusive_maximum_value` that hide the 3.0 boolean versus 3.1 numeric encoding. Fixes #6.

**Acceptance criteria:**
- [ ] 3.0 `{$ref, nullable: true}` is not nullable and has one diagnostic; 3.1 is nullable
- [ ] 3.0 `{minimum: 5, exclusiveMinimum: true}` and 3.1 `{exclusiveMinimum: 5}` give the same `exclusive_minimum_value`
- [ ] Twilio parses with siblings dropped (count recorded in the PR)

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_schema*.py tests/regressions -vv`
- [ ] Checks pass
- [ ] Finding #6 and the Twilio shim-diff xfails removed

**Dependencies:** 10

**Files likely touched:**
- `cicerone/spec/schema.py`
- `tests/spec/test_schema_dialects.py`
- `tests/regressions/test_findings.py`

**Estimated scope:** Small

## Task 15: pathItems, typed content, XML, webhooks

**Description:** Add `Components.path_items` (#10). Type `Parameter.content` and `Header.content` as `dict[str, MediaType]` and add `Parameter.allow_reserved` and `Header` 3.x fields. Add an `XML` model (3.0 to 3.2 fields minus `nodeType`, which lands in Task 29) and type `Schema.xml`. Webhooks stop using fake `webhook:<name>` paths: `PathItem.path` becomes `str | None` and webhook items are keyed by name.

**Acceptance criteria:**
- [ ] `components.pathItems` round-trips into typed `PathItem`s with locations
- [ ] `Parameter.content["application/json"].schema_` is a `Schema`
- [ ] No string `"webhook:"` anywhere in `cicerone/`

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec -vv`
- [ ] Checks pass
- [ ] Finding #10 xfail removed; matching conformance allowlist entries removed

**Dependencies:** 10

**Files likely touched:**
- `cicerone/spec/components.py`, `parameter.py`, `header.py`, `webhooks.py`
- `cicerone/spec/xml.py`

**Estimated scope:** Medium

## Checkpoint 4: Structurally correct 3.0 / 3.1
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Findings #1, #4 to #10 passing
- [ ] Review with human before proceeding

---

## Phase 5: Local references (spec PR 6)

## Task 16: Pointer module and `spec.resolve`

**Description:** Add `cicerone/pointer.py` with `parse(ref) -> (document, tokens)` doing RFC 3986 percent-decoding of the fragment then RFC 6901 unescaping (`~1` before `~0` order handled correctly), plus `escape()` and `join()`. Add `spec.resolve(ref, *, base=None, as_type=None)` that looks the location up in the index, returning the indexed model if there is one and the raw value otherwise. Fixes #2.

**Acceptance criteria:**
- [ ] All RFC 6901 section 5 example pointers resolve against the RFC's example document
- [ ] `#/paths/~1users~1{id}` returns the `PathItem`; `#/paths/%7Bid%7D`-style encoded fragments decode
- [ ] A missing target raises `RefResolutionError` with the did-you-mean hint the old resolver had

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references/test_pointer.py tests/references/test_resolve.py tests/regressions -vv`
- [ ] Checks pass
- [ ] Finding #2 xfail removed

**Dependencies:** 12, 13, 14, 15

**Files likely touched:**
- `cicerone/pointer.py`
- `cicerone/spec/openapi_spec.py`
- `tests/references/test_pointer.py`, `tests/references/test_resolve.py`

**Estimated scope:** Small

## Task 17: Referenceable models and `spec.deref`

**Description:** Add a `Referenceable` mixin giving `ref` and `is_ref` to Schema, Parameter, Response, RequestBody, Header, Example, Link, Callback, SecurityScheme and PathItem (Callback, Example, Link, SecurityScheme are new). `spec.deref(obj)` follows a ref chain to the canonical indexed object (identity with `spec.components.*`), shallow, with cycle detection raising `CircularReferenceError`. In 3.1+ a Reference Object's `summary` / `description` override the target's on a frozen copy. Unresolvable refs found during parse become `ref-unresolved` error diagnostics. Parameter override (Task 13) now matches dereferenced parameters.

**Acceptance criteria:**
- [ ] `spec.deref(op.request_body) is spec.components.request_bodies["B"]` for a one-hop ref
- [ ] Two-hop chains resolve; a two-node cycle raises `CircularReferenceError`
- [ ] 1Password shim-diff regression passes at the cicerone level (typed body and response reachable)

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references -vv tests/regressions -vv`
- [ ] Checks pass
- [ ] 1Password shim-diff xfail removed

**Dependencies:** 16

**Files likely touched:**
- `cicerone/spec/model_utils.py` (mixin)
- `cicerone/spec/callback.py`, `example.py`, `link.py`, `security_scheme.py`
- `cicerone/spec/openapi_spec.py`
- `tests/references/test_deref.py`

**Estimated scope:** Medium

## Task 18: Site-typed resolution

**Description:** The builder records the expected model type for every position where a Reference Object may appear. Derive the position list from Task 4's parsed tables (cells containing "Reference Object"), checked in as data, not hand-written. A `$ref` whose target is not already indexed as that type (a deep pointer, or later an external document) is built as the expected type at its target location on first `deref` and indexed. Fixes #3.

**Acceptance criteria:**
- [ ] `#/components/responses/R/content/application~1json/schema` derefs to a `Schema`
- [ ] A schema `$ref` to `#/components/schemas/S/properties/x` returns the indexed nested `Schema` (same identity)
- [ ] The position list is generated from the vendored spec tables and a test fails if they drift

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references -vv tests/regressions -vv`
- [ ] Checks pass
- [ ] Finding #3 xfail removed

**Dependencies:** 17

**Files likely touched:**
- `cicerone/spec/model_utils.py`
- `cicerone/references/positions.py` (generated data)
- `scripts/refresh_oai.py` (emit positions)
- `tests/references/test_site_typing.py`

**Estimated scope:** Medium

## Task 19: `component_key`, `references`, `is_recursive`; delete the old resolver

**Description:** Add `ComponentKey(kind, name, document)` and `spec.component_key(obj)`; `spec.references()` (every ref in the parsed graph with its location); `spec.is_recursive(schema)`. Delete `cicerone/references/reference_resolver.py`, `resolve_reference`, `get_all_references`, `is_circular_reference`, and rewrite `tests/spec/test_reference.py` against the new API. Freeze the remaining models. Fixes #11.

**Acceptance criteria:**
- [ ] `component_key(schema_with_ref_to_User)` returns `("schemas", "User", <root uri>)`; non-component objects return `None`
- [ ] Old resolver module and methods gone; every model frozen
- [ ] Finding #11 test passes (no second object graph, names survive)

**Verification:**
- [ ] Tests pass: `uv run pytest -vv`
- [ ] Checks pass
- [ ] Finding #11 xfail removed
- [ ] Manual check: `uv run python scripts/clientele_smoke.py ../clientele` against the C2 branch

**Dependencies:** 18

**Files likely touched:**
- `cicerone/spec/openapi_spec.py`
- `cicerone/references/` (resolver deleted; `reference.py` reduced to helpers or removed)
- `tests/spec/test_reference.py` (rewritten), `tests/references/test_component_key.py`

**Estimated scope:** Medium

## Checkpoint 5: Codegen-ready references
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Findings #1 to #11 passing
- [ ] Clientele C2 branch can replace `get_param_from_ref`, `get_schema_from_ref` and `schema_ref` with `deref` / `component_key`
- [ ] Review with human before proceeding

---

## Phase 6: OAS 3.1 Schema completeness (spec PR 7)

## Task 20: 3.1 Schema keywords

**Description:** Type and recursively parse `$defs`, `patternProperties`, `propertyNames`, `unevaluatedProperties`, `unevaluatedItems`, `contains`, `minContains`, `maxContains`, `dependentRequired`, `dependentSchemas`, `if`, `then`, `else`, `contentEncoding`, `contentMediaType`, `contentSchema`, `$comment`, `externalDocs` on `Schema`. Subschemas get locations and are indexed, so `#/components/schemas/S/$defs/Inner` derefs by identity.

**Acceptance criteria:**
- [ ] None of these keywords remain in `model_extra` after parsing
- [ ] Every subschema position is indexed and derefable
- [ ] Conformance allowlist has no remaining Schema entries other than `$id`, `$anchor`, `$schema`, `$dynamicRef`, `$dynamicAnchor`

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_schema*.py tests/conformance -vv`
- [ ] Checks pass

**Dependencies:** 19

**Files likely touched:**
- `cicerone/spec/schema.py`
- `tests/spec/test_schema_31_keywords.py`
- `tests/fixtures/oai/allowlist.toml`

**Estimated scope:** Small

## Task 21: `$id` / `$anchor`, `$dynamicRef`, Schema helpers

**Description:** Track base URIs inside a document: `$id` on a Schema sets the base for its subtree (resolved against the enclosing base per RFC 3986), `$anchor` registers a plain-name fragment, both indexed so refs to them resolve. `$dynamicRef` and `$dynamicAnchor` are typed and resolve like `$ref` / `$anchor` with a `dynamic-ref-unsupported` warning. Add `Schema.non_null_types`, `non_null_variants`, and `Responses.success()` / `.default` helpers. Closes the 3.1 multi-type shim-diff row.

**Acceptance criteria:**
- [ ] A ref to `https://example.com/schemas/pet#name` resolves when a subschema declares that `$id` and `$anchor`
- [ ] `non_null_variants` of `anyOf: [A, {type: null}]` is `[A]`; `non_null_types` of `["integer","string","null"]` is `["integer","string"]`
- [ ] Conformance allowlist has no Schema entries left

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references tests/spec tests/regressions -vv`
- [ ] Checks pass
- [ ] 3.1 multi-type shim-diff xfail removed

**Dependencies:** 20

**Files likely touched:**
- `cicerone/spec/schema.py`
- `cicerone/spec/model_utils.py`
- `cicerone/spec/response.py` (`Responses` helper)
- `tests/references/test_schema_ids.py`

**Estimated scope:** Medium

## Checkpoint 6: 3.1 complete
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Every shim-diff regression passing
- [ ] Review with human before proceeding

---

## Phase 7: External references (spec PR 8)

## Task 22: DocumentStore and file refs

**Description:** Add `cicerone/documents.py` with `Document(uri, raw, base_uri)` and `DocumentStore` (cache by absolute URI, load once, injectable `fetcher`). Resolve `$ref` URIs against the containing document's base per RFC 3986 section 5. Load referenced files on demand during parse; build their targets with site typing (Task 18) into the same index. Enforce containment: only paths under the root's directory or `allow_paths` entries, after `realpath` (symlinks cannot escape). Detect cycles across documents. `file://` is the only non-network scheme accepted.

**Acceptance criteria:**
- [ ] A spec split across `openapi.yaml`, `schemas/pet.yaml` (bare schema) and `params.yaml#/Limit` derefs to typed objects with correct locations
- [ ] `../../etc/passwd`-style and symlink escapes raise `RefResolutionError` without reading the file
- [ ] Cross-document cycles raise `CircularReferenceError` on `deref`, not during parse

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references/test_external.py -vv`
- [ ] Checks pass
- [ ] Manual check: security-focused read of the containment code by the human reviewer

**Dependencies:** 21

**Files likely touched:**
- `cicerone/documents.py`
- `cicerone/parse/parser.py`
- `cicerone/spec/openapi_spec.py`
- `tests/references/test_external.py`, `tests/fixtures/multifile/`

**Estimated scope:** Medium

## Task 23: Remote refs

**Description:** `http` and `https` refs load only with `allow_remote=True`; otherwise `RemoteRefDisallowedError` is raised from `deref` and an error diagnostic is recorded at parse. This applies even when the root came from `parse_url`. Remote fetches use the parse timeout and a size cap (default 20 MiB). Any other scheme is refused.

**Acceptance criteria:**
- [ ] Without `allow_remote`, no network call is attempted (fetcher spy asserts zero calls)
- [ ] With it, a ref into a local `http.server` resolves; oversized and slow responses fail cleanly
- [ ] `ftp:`, `data:` and unknown schemes are refused with a clear message

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references/test_remote.py -vv`
- [ ] Checks pass
- [ ] Manual check: security-focused review of defaults

**Dependencies:** 22

**Files likely touched:**
- `cicerone/documents.py`
- `cicerone/parse/parser.py`
- `tests/references/test_remote.py`

**Estimated scope:** Small

## Task 24: `named_schemas`

**Description:** `spec.named_schemas() -> dict[str, Schema]`: every schema with a component key, from the root and any loaded external documents, reachable from paths, webhooks or components. Naming: component name, else last pointer segment, else file stem. Order: root first, then documents by URI, then pointer. Collisions keep the first; later ones get the PascalCase document stem prefixed (`ModelsPet`) and a `schema-name-collision` warning.

**Acceptance criteria:**
- [ ] Single-document spec: result equals `components.schemas` in order
- [ ] Two documents both defining `Pet`: `Pet` (root) and `ModelsPet` (from `models.yaml`), one diagnostic
- [ ] Output is deterministic across runs and platforms

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references/test_named_schemas.py -vv`
- [ ] Checks pass

**Dependencies:** 22

**Files likely touched:**
- `cicerone/spec/openapi_spec.py`
- `tests/references/test_named_schemas.py`

**Estimated scope:** Small

## Task 25: `bundle()`

**Description:** `spec.bundle() -> dict` returns a single self-contained document: external targets hoisted into the right `components` map under their `named_schemas()` (or equivalent per-kind) names, every ref rewritten to a local pointer, `$self` dropped. Round-trip: `parse_dict(spec.bundle())` yields a model graph equal to the original apart from locations.

**Acceptance criteria:**
- [ ] Bundled multi-file fixture contains no external refs
- [ ] Round-trip equality holds for every multi-file fixture and every single-file realworld fixture
- [ ] Non-schema external targets (parameters, responses) hoist into their own components maps

**Verification:**
- [ ] Tests pass: `uv run pytest tests/references/test_bundle.py -vv`
- [ ] Checks pass

**Dependencies:** 24

**Files likely touched:**
- `cicerone/bundle.py`
- `cicerone/spec/openapi_spec.py`
- `tests/references/test_bundle.py`

**Estimated scope:** Medium

## Checkpoint 7: Multi-document specs
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Security review of Tasks 22 and 23 done by the human
- [ ] Clientele C2 branch generates from a multi-file fixture via `named_schemas`
- [ ] Review with human before proceeding

---

## Phase 8: OAS 3.2 (spec PR 9)

## Task 26: 3.2 document level

**Description:** `OpenAPISpec.self_uri` (`$self`) becomes the root document's base URI when present, resolved against the retrieval URI. `Server.name`. `Tag.summary`, `parent`, `kind`, plus `spec.tag_tree()` with diagnostics for unknown parents and cycles.

**Acceptance criteria:**
- [ ] A relative ref resolves against `$self` rather than the file path when both exist
- [ ] `tag_tree()` returns roots with children in document order; a cycle produces one diagnostic and no infinite loop
- [ ] Conformance allowlist entries for OpenAPI, Server and Tag removed

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_tag.py tests/spec/test_server.py tests/references -vv tests/conformance -vv`
- [ ] Checks pass

**Dependencies:** 22

**Files likely touched:**
- `cicerone/spec/openapi_spec.py`, `server.py`, `tag.py`
- `cicerone/documents.py`

**Estimated scope:** Small

## Task 27: 3.2 operations

**Description:** `PathItem` parses `query` into `operations["query"]` and `additionalOperations` into `operations` keyed by the original method string; `Operation.method` keeps the wire case. QUERY is included in `all_operations`, `operations_by_tag` and `operation_by_operation_id`, and allows a request body. `in: querystring` parameters are accepted; combining one with `query` parameters in the same operation, or using it without `content`, produces a diagnostic. Additional operations that repeat a fixed-field method produce a diagnostic.

**Acceptance criteria:**
- [ ] `operations` for a 3.2 path with `get`, `query` and `additionalOperations: {COPY: ...}` has three entries with methods `GET`, `QUERY`, `COPY`
- [ ] QUERY operations appear in tag lookups
- [ ] `querystring` rules produce the documented diagnostics

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_path_item.py tests/spec/test_operation.py tests/spec/test_query_api.py tests/conformance -vv`
- [ ] Checks pass

**Dependencies:** 26

**Files likely touched:**
- `cicerone/spec/path_item.py`, `operation.py`, `parameter.py`, `openapi_spec.py`
- `tests/spec/test_oas32_operations.py`

**Estimated scope:** Medium

## Task 28: 3.2 media types

**Description:** `MediaType.item_schema`, `prefix_encoding`, `item_encoding`, `ref`; `Encoding` gains nested `encoding`, `prefix_encoding`, `item_encoding`; `Components.media_types`. `MediaType.is_sequential` is true for `text/event-stream`, `application/jsonl`, `application/x-ndjson`, `application/json-seq` and any `+json-seq` suffix. A diagnostic when `encoding` coexists with a positional field. MediaType becomes Referenceable.

**Acceptance criteria:**
- [ ] A `text/event-stream` response with `itemSchema` exposes a typed `Schema` at `item_schema`
- [ ] `components.mediaTypes` refs deref to `MediaType`
- [ ] Conformance allowlist entries for Media Type, Encoding and Components removed

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec/test_media_type.py tests/references tests/conformance -vv`
- [ ] Checks pass

**Dependencies:** 26

**Files likely touched:**
- `cicerone/spec/media_type.py`, `encoding.py`, `components.py`
- `tests/spec/test_media_type.py`

**Estimated scope:** Small

## Task 29: 3.2 remaining objects

**Description:** `Response.summary` and optional `description` in 3.2 (missing `description` in 3.0 / 3.1 is a diagnostic); `Example.data_value`, `serialized_value`; `Discriminator.default_mapping`; `SecurityScheme.deprecated`, `oauth2_metadata_url`; `OAuthFlows.device_authorization` and `OAuthFlow.device_authorization_url`; `XML.node_type`.

**Acceptance criteria:**
- [ ] Every 3.2.1 fixed-field row is typed; field-coverage allowlist is empty
- [ ] Missing Response `description` warns in 3.0 / 3.1 and is silent in 3.2
- [ ] Device authorization flow parses with its URL

**Verification:**
- [ ] Tests pass: `uv run pytest tests/spec tests/conformance -vv`
- [ ] Checks pass

**Dependencies:** 26

**Files likely touched:**
- `cicerone/spec/response.py`, `example.py`, `discriminator.py`, `security_scheme.py`, `oauth_flows.py`
- `cicerone/spec/xml.py`

**Estimated scope:** Medium

## Task 30: `field-not-in-dialect` diagnostics

**Description:** Using the field-to-version data from Task 4's tables, emit a `field-not-in-dialect` warning when a document uses a field newer than its declared version (for example `itemSchema` in a 3.1 document). The field is still parsed and typed.

**Acceptance criteria:**
- [ ] `query` in a 3.1 document: parsed, one warning at its location
- [ ] No warnings for any vendored spec example in its own version
- [ ] Field-to-version data is generated, not hand-maintained

**Verification:**
- [ ] Tests pass: `uv run pytest tests/test_diagnostics.py tests/conformance -vv`
- [ ] Checks pass

**Dependencies:** 27, 28, 29

**Files likely touched:**
- `cicerone/spec/model_utils.py`
- `cicerone/spec/dialect_fields.py` (generated)
- `scripts/refresh_oai.py`

**Estimated scope:** Small

## Checkpoint 8: 3.2 complete
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Field-coverage allowlist empty
- [ ] Review with human before proceeding

---

## Phase 9: Hardening (spec PR 10, part 1)

## Task 31: Hypothesis fuzz test

**Description:** A Hypothesis strategy generating JSON-like documents seeded from real spec shapes (valid `openapi` header, random objects, wrong types, deep nesting, random `$ref` strings). Lenient parsing never raises anything except `UnsupportedVersionError` and root I/O errors; strict parsing raises only `ParseError`.

**Acceptance criteria:**
- [ ] 2,000 examples in CI without failures; a nightly-style profile with more examples available via `HYPOTHESIS_PROFILE`
- [ ] Any bug it finds is fixed with a pinned `@example`

**Verification:**
- [ ] Tests pass: `uv run pytest tests/test_fuzz.py -vv`
- [ ] Checks pass

**Dependencies:** 30

**Files likely touched:**
- `tests/test_fuzz.py`
- `tests/conftest.py` (profiles)

**Estimated scope:** Small

## Task 32: Corpus script and badge

**Description:** Move `test_openapi_directory.py` to `scripts/corpus.py`. Parse every 3.x spec in a local APIs.guru checkout (Swagger 2.0 counted separately, not as failures). Report parse rate, ref-resolution rate (every ref `deref`-ed), and a diagnostics histogram as JSON. `--fail-under` gates on parse and ref rates. The weekly workflow writes `.github/compatibility.json` from that JSON, fixing #13.

**Acceptance criteria:**
- [ ] JSON output with counts, rates and top diagnostic codes; human summary on stderr
- [ ] Workflow writes a real percentage; no `sed` over log text
- [ ] Baseline numbers recorded in the PR

**Verification:**
- [ ] Manual check: `uv run python scripts/corpus.py --directory /path/to/openapi-directory --json out.json`
- [ ] Finding #13 test passes against a sample output file
- [ ] Checks pass

**Dependencies:** 30

**Files likely touched:**
- `scripts/corpus.py` (moved from `test_openapi_directory.py`)
- `.github/workflows/test-openapi-directory.yml`
- `tests/regressions/test_findings.py`

**Estimated scope:** Small

## Task 33: Corpus fixes

**Description:** Work the Task 32 histogram until the corpus reaches 99.5% parse and 99% ref resolution. Each fix ships with a minimal regression test extracted from the failing spec, not the spec itself.

**Acceptance criteria:**
- [ ] `scripts/corpus.py --fail-under-parse 99.5 --fail-under-refs 99` passes
- [ ] Every fix has a minimal test

**Verification:**
- [ ] Tests pass: `uv run pytest -vv`
- [ ] Manual check: corpus run output attached to the PR
- [ ] Checks pass

**Dependencies:** 32

**Files likely touched:**
- Varies; keep each commit to one root cause and at most five files

**Estimated scope:** Medium (open-ended: split by root cause if it grows)

## Task 34: Performance benchmarks

**Description:** Extend `tests/test_performance.py` with Twilio (~26k lines) parse plus a full `deref` walk, compared against a recorded 0.3.0 baseline. Optimise index and context hot paths if over the ceiling.

**Acceptance criteria:**
- [ ] Twilio parse time at most 1.5x the 0.3.0 baseline on the same machine
- [ ] Baseline numbers and method recorded in the test module docstring

**Verification:**
- [ ] Tests pass: `uv run pytest tests/test_performance.py --benchmark-only`
- [ ] Checks pass

**Dependencies:** 30

**Files likely touched:**
- `tests/test_performance.py`
- Hot paths in `cicerone/context.py`, `cicerone/spec/model_utils.py` if needed

**Estimated scope:** Small

## Checkpoint 9: Release gates green
- [ ] All tests pass, checks clean, coverage not lower than the previous checkpoint and new code fully covered
- [ ] Corpus at or above 99.5% / 99%; fuzz clean; performance within ceiling
- [ ] Review with human before proceeding

---

## Phase 10: Release (spec PR 10, part 2)

## Task 35: Docs rewrite

**Description:** Rewrite `README.md` and `docs/` for the 0.5.0 API: parsing and options, diagnostics and every diagnostic code, references (`deref`, `resolve`, `component_key`, `named_schemas`, `bundle`), external ref security defaults, version semantics table, 3.2 features. Remove the 0.4.0 migration notes; add a short "upgrading from 0.3.0" page aimed at clientele.

**Acceptance criteria:**
- [ ] Every code sample runs (doctest or a test that executes the README blocks)
- [ ] Every diagnostic code emitted by the code is documented, checked by a test
- [ ] `mkdocs build --strict` passes

**Verification:**
- [ ] Tests pass: `uv run pytest tests/test_docs.py -vv`
- [ ] Manual check: `uv run mkdocs build --strict`
- [ ] Checks pass

**Dependencies:** 30

**Files likely touched:**
- `README.md`
- `docs/index.md`, `docs/parser.md`, `docs/references.md`, `docs/models.md`, `docs/compatibility.md`
- `docs/diagnostics.md`, `docs/upgrading.md`, `mkdocs.yml`, `tests/test_docs.py`

**Estimated scope:** Medium

## Task 36: Ratchets at zero

**Description:** Assert both conformance allowlists are empty, except example blocks the human has signed off as non-parseable by design (prose fragments or deliberately invalid snippets), each with a reason. Assert no `xfail` markers remain in `tests/regressions`. Make the `clientele_smoke.py` CI job blocking, pointed at the clientele C2 branch.

**Acceptance criteria:**
- [ ] Field-coverage allowlist empty; example allowlist contains only signed-off entries
- [ ] `grep -rn xfail tests/regressions` returns nothing
- [ ] Smoke job blocking and green

**Verification:**
- [ ] Tests pass: `uv run pytest -vv`
- [ ] Checks pass

**Dependencies:** 31, 33, 34

**Files likely touched:**
- `tests/fixtures/oai/allowlist.toml`
- `tests/conformance/*.py`
- `.github/workflows/ci.yml`

**Estimated scope:** Small

## Task 37: CHANGELOG and release

**Description:** Bump to 0.5.0. Replace the unreleased 0.4.0 CHANGELOG section with a 0.5.0 entry covering everything above, written for a reader upgrading from 0.3.0. Follow `PUBLISHING.md` to build and publish. Tag `0.5.0`.

**Acceptance criteria:**
- [ ] `cicerone==0.5.0` installable from PyPI
- [ ] CHANGELOG has no 0.4.0 section; 0.5.0 lists breaking changes first
- [ ] Tag pushed

**Verification:**
- [ ] Manual check: `uv pip install cicerone==0.5.0` in a clean venv, then `python -c "import cicerone; print(cicerone.__version__)"`
- [ ] Checks pass

**Dependencies:** 35, 36

**Files likely touched:**
- `pyproject.toml`, `uv.lock`
- `CHANGELOG.md`, `docs/CHANGELOG.md`

**Estimated scope:** Small

## Checkpoint 10: Complete
- [ ] Every spec Success Criterion met except the clientele ones (tracked in clientele C1 to C4)
- [ ] 0.5.0 on PyPI
- [ ] Hand-off to clientele C2 with the smoke baseline
