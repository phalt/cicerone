"""Regression tests for every defect in specs/SPEC-cicerone-next.md ("Defects on main").

Each test asserts the behaviour the spec asks for, through the API the spec
defines, so several call methods that do not exist yet. Until its fix lands a
test is a strict xfail pinned to the exception it raises today: a test that
starts passing must have its marker removed, and a test that fails some other
way errors instead of hiding as an expected failure. Calls to APIs that do
not exist yet carry a ``ty: ignore[unresolved-attribute]``; delete it with the
xfail marker (ty flags the suppression as unused once the API exists).

Finding #12 (stale settings.VERSION) was fixed in Task 2 and is covered by
tests/test_package.py. Finding #13 (corpus badge) is tested where the corpus
script lands, in Task 32.
"""

from __future__ import annotations

import typing

import pydantic
import pytest

from cicerone import Response, UnsupportedVersionError, parse_spec_from_dict

# Raised by pytest.raises when the expected exception never happens
DID_NOT_RAISE = pytest.fail.Exception


def finding(label: str, *, raises: type[BaseException] | tuple[type[BaseException], ...]) -> pytest.MarkDecorator:
    """Mark a test as a known defect from the spec, failing in exactly the given way until fixed."""
    return pytest.mark.xfail(strict=True, raises=raises, reason=label)


def document(version: str = "3.0.3", **parts: typing.Any) -> dict[str, typing.Any]:
    """Build the smallest valid document, with the given top-level parts."""
    return {"openapi": version, "info": {"title": "t", "version": "1"}, "paths": {}, **parts}


@finding("Finding #1: Swagger 2.0 is reported as 3.0.0", raises=DID_NOT_RAISE)
def test_finding_1_swagger_2_is_rejected() -> None:
    with pytest.raises(UnsupportedVersionError):
        parse_spec_from_dict({"swagger": "2.0", "info": {"title": "t", "version": "1"}, "paths": {}})


@finding("Finding #1: a missing openapi key defaults to 3.0.0", raises=DID_NOT_RAISE)
def test_finding_1_missing_openapi_key_is_rejected() -> None:
    with pytest.raises(UnsupportedVersionError):
        parse_spec_from_dict({"info": {"title": "t", "version": "1"}, "paths": {}})


@finding("Finding #2: RFC 6901 ~1 and ~0 escapes are not decoded", raises=AttributeError)
def test_finding_2_escaped_pointers_resolve() -> None:
    spec = parse_spec_from_dict(
        document(paths={"/users/{id}": {"get": {"responses": {"200": {"description": "ok"}}}}, "/a~b": {}})
    )

    assert spec.resolve("#/paths/~1users~1{id}") is spec.paths["/users/{id}"]  # ty: ignore[unresolved-attribute]
    assert spec.resolve("#/paths/~1a~0b") is spec.paths["/a~b"]  # ty: ignore[unresolved-attribute]


@finding("Finding #3: deep pointers are typed by their path prefix", raises=AttributeError)
def test_finding_3_deep_pointer_returns_the_nested_object() -> None:
    spec = parse_spec_from_dict(
        document(
            components={
                "responses": {
                    "R": {"description": "r", "content": {"application/json": {"schema": {"type": "integer"}}}}
                }
            }
        )
    )
    response = spec.components.responses["R"]

    assert spec.resolve("#/components/responses/R/content/application~1json/schema") is (  # ty: ignore[unresolved-attribute]
        response.content["application/json"].schema_
    )
    # The defect: anything under /components/responses came back as a Response
    assert not isinstance(spec.resolve("#/components/responses/R/content"), Response)  # ty: ignore[unresolved-attribute]


@finding("Finding #4: path-level params are not overridden by operation-level ones", raises=AssertionError)
def test_finding_4_operation_parameter_overrides_path_parameter() -> None:
    spec = parse_spec_from_dict(
        document(
            paths={
                "/x": {
                    "parameters": [{"name": "q", "in": "query", "schema": {"type": "string"}}],
                    "get": {
                        "parameters": [{"name": "q", "in": "query", "required": True, "schema": {"type": "integer"}}],
                        "responses": {"200": {"description": "ok"}},
                    },
                }
            }
        )
    )

    parameters = spec.paths["/x"].operations["get"].parameters
    assert [(p.name, p.schema_.type if p.schema_ else None) for p in parameters] == [("q", "integer")]


@finding("Finding #5: x- keys under paths are parsed as paths", raises=AssertionError)
def test_finding_5_extension_keys_under_paths_are_not_paths() -> None:
    spec = parse_spec_from_dict(document(paths={"x-meta": {"owner": "team"}, "/a": {}}))

    assert "x-meta" not in spec.paths
    assert spec.paths.extensions == {"x-meta": {"owner": "team"}}  # ty: ignore[unresolved-attribute]


@finding("Finding #6: 3.0 $ref siblings are not ignored", raises=AssertionError)
def test_finding_6_ref_siblings_are_ignored_in_3_0() -> None:
    spec = parse_spec_from_dict(
        document(
            "3.0.3",
            components={
                "schemas": {
                    "E": {"type": "string", "enum": ["a"]},
                    "M": {
                        "type": "object",
                        "properties": {"e": {"$ref": "#/components/schemas/E", "nullable": True}},
                    },
                }
            },
        )
    )

    assert not spec.components.schemas["M"].properties["e"].is_nullable


@finding("Finding #7: lenient fallbacks drop values without recording anything", raises=AttributeError)
def test_finding_7_lenient_fallback_records_a_diagnostic() -> None:
    spec = parse_spec_from_dict(
        document(components={"schemas": {"S": {"type": "object", "required": True, "properties": {}}}})
    )

    assert spec.components.schemas["S"].required == []
    assert any(
        d.code == "invalid-value" and d.location.pointer == "/components/schemas/S/required"
        for d in spec.diagnostics  # ty: ignore[unresolved-attribute]
    )


@finding("Finding #8: a discriminator without propertyName aborts the parse", raises=pydantic.ValidationError)
def test_finding_8_discriminator_without_property_name_is_dropped() -> None:
    spec = parse_spec_from_dict(
        document(components={"schemas": {"S": {"oneOf": [{"type": "string"}], "discriminator": {"mapping": {}}}}})
    )

    assert spec.components.schemas["S"].discriminator is None


@finding("Finding #9: a non-dict operation aborts the parse", raises=AttributeError)
def test_finding_9_non_dict_operation_is_skipped() -> None:
    spec = parse_spec_from_dict(
        document(paths={"/a": {"get": "oops", "post": {"responses": {"200": {"description": "ok"}}}}})
    )

    assert list(spec.paths["/a"].operations) == ["post"]


@finding("Finding #10: components.pathItems is dropped", raises=AttributeError)
def test_finding_10_components_path_items_are_parsed() -> None:
    spec = parse_spec_from_dict(
        document("3.1.0", components={"pathItems": {"P": {"get": {"responses": {"200": {"description": "ok"}}}}}})
    )

    assert list(spec.components.path_items["P"].operations) == ["get"]  # ty: ignore[unresolved-attribute]


@finding("Finding #11: resolving a ref builds a second, inlined object graph", raises=AttributeError)
def test_finding_11_deref_returns_the_canonical_component() -> None:
    spec = parse_spec_from_dict(
        document(
            paths={
                "/a": {
                    "post": {
                        "requestBody": {"$ref": "#/components/requestBodies/B"},
                        "responses": {"200": {"description": "ok"}},
                    }
                }
            },
            components={
                "requestBodies": {
                    "B": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/S"}}}}
                },
                "schemas": {"S": {"type": "object"}},
            },
        )
    )
    operation = spec.paths["/a"].operations["post"]

    body = spec.deref(operation.request_body)  # ty: ignore[unresolved-attribute]

    assert body is spec.components.request_bodies["B"]
    # The nested schema ref is kept, so codegen can still name the class
    assert body.content["application/json"].schema_.ref == "#/components/schemas/S"


# Rows from the spec's "Generator output, shim versus no shim" table, asserted at the cicerone level


@finding("Shim diff: Twilio-style $ref with sibling type and nullable under 3.0", raises=AssertionError)
def test_shim_diff_twilio_ref_wins_over_siblings_in_3_0() -> None:
    spec = parse_spec_from_dict(
        document(
            "3.0.3",
            components={
                "schemas": {
                    "call_enum_status": {"type": "string", "enum": ["queued", "ringing"]},
                    "Call": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "$ref": "#/components/schemas/call_enum_status",
                                "type": "string",
                                "nullable": True,
                            }
                        },
                    },
                }
            },
        )
    )

    status = spec.components.schemas["Call"].properties["status"]
    assert status.ref == "#/components/schemas/call_enum_status"
    assert status.type is None
    assert not status.is_nullable


@finding("Shim diff: 1Password-style requestBody and response refs are not dereferenceable", raises=AttributeError)
def test_shim_diff_1password_body_and_response_refs_deref_to_typed_objects() -> None:
    spec = parse_spec_from_dict(
        document(
            paths={
                "/api/v1/auditevents": {
                    "post": {
                        "requestBody": {"$ref": "#/components/requestBodies/AuditEventsRequest"},
                        "responses": {"200": {"$ref": "#/components/responses/AuditEventsResponse"}},
                    }
                }
            },
            components={
                "requestBodies": {
                    "AuditEventsRequest": {
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Cursor"}}}
                    }
                },
                "responses": {
                    "AuditEventsResponse": {
                        "description": "events",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Events"}}},
                    }
                },
                "schemas": {"Cursor": {"type": "object"}, "Events": {"type": "array", "items": {"type": "object"}}},
            },
        )
    )
    operation = spec.paths["/api/v1/auditevents"].operations["post"]

    body = spec.deref(operation.request_body)  # ty: ignore[unresolved-attribute]
    response = spec.deref(operation.responses["200"])  # ty: ignore[unresolved-attribute]

    assert body.content["application/json"].schema_.ref == "#/components/schemas/Cursor"
    assert response.content["application/json"].schema_.ref == "#/components/schemas/Events"


@finding("Shim diff: 3.1 multi-type arrays collapse to the first type", raises=AttributeError)
def test_shim_diff_3_1_multi_type_keeps_every_non_null_type() -> None:
    spec = parse_spec_from_dict(
        document("3.1.0", components={"schemas": {"S": {"type": ["integer", "string", "null"]}}})
    )

    schema = spec.components.schemas["S"]
    assert schema.non_null_types == ["integer", "string"]  # ty: ignore[unresolved-attribute]
    assert schema.is_nullable
