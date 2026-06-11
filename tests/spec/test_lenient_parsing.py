"""Tests for lenient parsing of malformed real-world specs.

Before 0.4.0, keywords like ``pattern`` or ``enum`` lived in ``model_extra``
and were never validated, so malformed values (e.g. a YAML float for
``pattern``) parsed fine. Promoting them to typed fields must not reject
documents 0.3.0 accepted: when an optional scalar field fails validation, the
field falls back to its default and the raw value remains available via
``model_extra`` (where mirrored) and ``spec.raw``.
"""

from __future__ import annotations

from cicerone import spec as cicerone_spec


class TestSchemaLenientScalars:
    def test_non_string_pattern_falls_back(self):
        # Seen in the wild: YAML parses `pattern: 0.0` as a float
        schema = cicerone_spec.Schema.from_dict({"type": "string", "pattern": 0.0})
        assert schema.pattern is None
        assert schema.model_extra is not None
        assert schema.model_extra["pattern"] == 0.0

    def test_non_list_enum_falls_back(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "enum": "red"})
        assert schema.enum is None
        assert schema.model_extra is not None
        assert schema.model_extra["enum"] == "red"

    def test_swagger2_style_boolean_required_falls_back(self):
        # Swagger 2.0 style `required: true` on a property-level schema
        schema = cicerone_spec.Schema.from_dict({"type": "string", "required": True})
        assert schema.required == []

    def test_non_numeric_minimum_falls_back(self):
        schema = cicerone_spec.Schema.from_dict({"type": "number", "minimum": "zero"})
        assert schema.minimum is None

    def test_non_string_format_falls_back(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "format": 64})
        assert schema.format is None

    def test_valid_values_still_validated(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "pattern": "^[a-z]+$", "minLength": 1})
        assert schema.pattern == "^[a-z]+$"
        assert schema.min_length == 1


class TestOperationLenientParsing:
    def test_malformed_inline_response_description(self):
        # 0.3.0 stored responses as raw dicts, so a non-string description
        # parsed fine; typed parsing must not reject the document
        data = {"responses": {"200": {"description": 200}}}
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        assert operation.responses["200"].description is None

    def test_malformed_inline_parameter_style(self):
        data = {"parameters": [{"name": "q", "in": "query", "style": 123}]}
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        assert operation.parameters[0].name == "q"
        assert operation.parameters[0].style is None

    def test_malformed_operation_summary(self):
        operation = cicerone_spec.Operation.from_dict("GET", "/users", {"summary": ["not", "a", "string"]})
        assert operation.summary is None

    def test_malformed_tags(self):
        operation = cicerone_spec.Operation.from_dict("GET", "/users", {"tags": "user"})
        assert operation.tags == []


class TestCollectionGuards:
    def test_non_string_property_keys_coerced(self):
        # YAML parses unquoted `no:` as boolean False; coerce keys to str
        schema = cicerone_spec.Schema.from_dict(
            {"type": "object", "properties": {False: {"type": "string"}, "name": {"type": "string"}}}
        )
        assert "False" in schema.properties
        assert "name" in schema.properties

    def test_boolean_properties_value_skipped(self):
        schema = cicerone_spec.Schema.from_dict({"type": "object", "properties": True})
        assert schema.properties == {}

    def test_non_string_header_keys_coerced(self):
        response = cicerone_spec.Response.from_dict(
            {"description": "OK", "headers": {False: {"schema": {"type": "string"}}}}
        )
        assert "False" in response.headers

    def test_malformed_example_summary(self):
        # Seen in the wild: YAML bool or date where a summary string belongs
        example = cicerone_spec.Example.from_dict({"summary": False, "value": 1})
        assert example.summary is None
        assert example.value == 1

    def test_non_dict_collection_items_skipped(self):
        # A malformed header entry must not crash parsing of the response
        response = cicerone_spec.Response.from_dict(
            {
                "description": "OK",
                "headers": {"X-Good": {"schema": {"type": "integer"}}, "X-Bad": "not-a-header"},
            }
        )
        assert "X-Good" in response.headers
        assert "X-Bad" not in response.headers


class TestHeaderAndRequestBodyLenient:
    def test_malformed_header_description(self):
        header = cicerone_spec.Header.from_dict({"description": {"text": "wrong shape"}})
        assert header.description is None

    def test_malformed_request_body_description(self):
        request_body = cicerone_spec.RequestBody.from_dict({"description": 123, "required": "yes-please"})
        assert request_body.description is None
        assert request_body.required is False
