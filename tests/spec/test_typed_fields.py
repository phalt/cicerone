"""Tests for the typed first-class fields introduced in 0.4.0.

These tests encode the contract that spec-defined fields (previously only
available via ``model_extra``) are now proper typed model fields, while raw
values remain mirrored in ``model_extra`` for backwards compatibility
(the mirroring is deprecated and will be removed in 0.5.0).
"""

from __future__ import annotations

from cicerone import spec as cicerone_spec
from cicerone.parse import parse_spec_from_dict


class TestSchemaTypedFields:
    """Schema exposes JSON Schema / OpenAPI keywords as typed fields."""

    def test_ref_field(self):
        schema = cicerone_spec.Schema.from_dict({"$ref": "#/components/schemas/User"})
        assert schema.ref == "#/components/schemas/User"

    def test_ref_defaults_to_none(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string"})
        assert schema.ref is None

    def test_format_field(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "format": "date-time"})
        assert schema.format == "date-time"

    def test_enum_field(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "enum": ["red", "green", "blue"]})
        assert schema.enum == ["red", "green", "blue"]

    def test_enum_defaults_to_none(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string"})
        assert schema.enum is None

    def test_default_field(self):
        schema = cicerone_spec.Schema.from_dict({"type": "integer", "default": 42})
        assert schema.default == 42
        assert schema.has_default

    def test_default_null_is_distinguished_from_absent(self):
        with_null_default = cicerone_spec.Schema.from_dict({"type": "string", "default": None})
        without_default = cicerone_spec.Schema.from_dict({"type": "string"})
        assert with_null_default.has_default
        assert with_null_default.default is None
        assert not without_default.has_default

    def test_const_field(self):
        schema = cicerone_spec.Schema.from_dict({"const": "fixed-value"})
        assert schema.const == "fixed-value"
        assert schema.has_const

    def test_const_null_is_distinguished_from_absent(self):
        with_null_const = cicerone_spec.Schema.from_dict({"const": None})
        without_const = cicerone_spec.Schema.from_dict({"type": "string"})
        assert with_null_const.has_const
        assert not without_const.has_const

    def test_deprecated_field(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "deprecated": True})
        assert schema.deprecated is True
        assert cicerone_spec.Schema.from_dict({"type": "string"}).deprecated is False

    def test_nullable_field(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "nullable": True})
        assert schema.nullable is True
        assert cicerone_spec.Schema.from_dict({"type": "string"}).nullable is None

    def test_read_only_and_write_only(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "readOnly": True, "writeOnly": False})
        assert schema.read_only is True
        assert schema.write_only is False

    def test_example_field(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "example": "hello"})
        assert schema.example == "hello"

    def test_numeric_constraints(self):
        schema = cicerone_spec.Schema.from_dict({"type": "number", "minimum": 0, "maximum": 100, "multipleOf": 0.5})
        assert schema.minimum == 0
        assert schema.maximum == 100
        assert schema.multiple_of == 0.5

    def test_exclusive_bounds_as_bool_openapi_30(self):
        schema = cicerone_spec.Schema.from_dict(
            {"type": "number", "minimum": 0, "exclusiveMinimum": True, "exclusiveMaximum": False}
        )
        assert schema.exclusive_minimum is True
        assert schema.exclusive_maximum is False

    def test_exclusive_bounds_as_number_openapi_31(self):
        schema = cicerone_spec.Schema.from_dict({"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 10})
        assert schema.exclusive_minimum == 0
        assert schema.exclusive_maximum == 10

    def test_string_constraints(self):
        schema = cicerone_spec.Schema.from_dict(
            {"type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-z]+$"}
        )
        assert schema.min_length == 1
        assert schema.max_length == 64
        assert schema.pattern == "^[a-z]+$"

    def test_array_constraints(self):
        schema = cicerone_spec.Schema.from_dict(
            {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 10, "uniqueItems": True}
        )
        assert schema.min_items == 1
        assert schema.max_items == 10
        assert schema.unique_items is True

    def test_object_constraints(self):
        schema = cicerone_spec.Schema.from_dict({"type": "object", "minProperties": 1, "maxProperties": 5})
        assert schema.min_properties == 1
        assert schema.max_properties == 5

    def test_additional_properties_as_schema(self):
        schema = cicerone_spec.Schema.from_dict({"type": "object", "additionalProperties": {"type": "string"}})
        assert isinstance(schema.additional_properties, cicerone_spec.Schema)
        assert schema.additional_properties.type == "string"

    def test_additional_properties_as_bool(self):
        closed = cicerone_spec.Schema.from_dict({"type": "object", "additionalProperties": False})
        open_ = cicerone_spec.Schema.from_dict({"type": "object", "additionalProperties": True})
        assert closed.additional_properties is False
        assert open_.additional_properties is True

    def test_additional_properties_absent(self):
        schema = cicerone_spec.Schema.from_dict({"type": "object"})
        assert schema.additional_properties is None

    def test_boolean_items_does_not_crash(self):
        # JSON Schema allows boolean schemas; cicerone skips them rather than crashing
        schema = cicerone_spec.Schema.from_dict({"type": "array", "items": True})
        assert schema.items is None

    def test_construction_by_field_name(self):
        # populate_by_name allows programmatic construction with snake_case names
        schema = cicerone_spec.Schema(ref="#/components/schemas/User", min_length=3)
        assert schema.ref == "#/components/schemas/User"
        assert schema.min_length == 3


class TestSchemaExtrasMirroring:
    """Promoted keys remain mirrored in model_extra until 0.5.0."""

    def test_scalar_keys_mirrored(self):
        data = {
            "$ref": "#/components/schemas/User",
            "enum": ["a", "b"],
            "default": "a",
            "const": "a",
            "deprecated": True,
            "format": "uuid",
        }
        schema = cicerone_spec.Schema.from_dict(data)
        extra = schema.model_extra
        assert extra["$ref"] == "#/components/schemas/User"
        assert extra["enum"] == ["a", "b"]
        assert extra["default"] == "a"
        assert extra["const"] == "a"
        assert extra["deprecated"] is True
        assert extra["format"] == "uuid"

    def test_mirrored_values_are_raw_not_models(self):
        data = {"discriminator": {"propertyName": "petType"}, "additionalProperties": {"type": "string"}}
        schema = cicerone_spec.Schema.from_dict(data)
        assert schema.model_extra["discriminator"] == {"propertyName": "petType"}
        assert schema.model_extra["additionalProperties"] == {"type": "string"}

    def test_absent_keys_not_mirrored(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string"})
        assert "enum" not in schema.model_extra
        assert "$ref" not in schema.model_extra

    def test_vendor_extensions_still_in_extras(self):
        schema = cicerone_spec.Schema.from_dict({"type": "string", "x-internal": True})
        assert schema.model_extra["x-internal"] is True


class TestOperationTypedFields:
    """Operation exposes requestBody, security, callbacks, etc. as typed fields."""

    def test_request_body_typed(self):
        data = {
            "operationId": "createUser",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"type": "object"}}},
            },
            "responses": {"201": {"description": "Created"}},
        }
        operation = cicerone_spec.Operation.from_dict("POST", "/users", data)
        assert isinstance(operation.request_body, cicerone_spec.RequestBody)
        assert operation.request_body.required is True
        media_type = operation.request_body.content["application/json"]
        assert isinstance(media_type.schema_, cicerone_spec.Schema)
        assert media_type.schema_.type == "object"

    def test_request_body_defaults_to_none(self):
        operation = cicerone_spec.Operation.from_dict("GET", "/users", {"operationId": "listUsers"})
        assert operation.request_body is None

    def test_responses_typed(self):
        data = {
            "responses": {
                "200": {
                    "description": "OK",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
                },
                "404": {"$ref": "#/components/responses/NotFound"},
            }
        }
        operation = cicerone_spec.Operation.from_dict("GET", "/users/{id}", data)
        ok = operation.responses["200"]
        assert isinstance(ok, cicerone_spec.Response)
        assert ok.description == "OK"
        assert ok.content["application/json"].schema_.ref == "#/components/schemas/User"
        not_found = operation.responses["404"]
        assert isinstance(not_found, cicerone_spec.Response)
        assert not_found.ref == "#/components/responses/NotFound"

    def test_parameters_typed(self):
        data = {
            "parameters": [
                {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                {"$ref": "#/components/parameters/PageSize"},
            ]
        }
        operation = cicerone_spec.Operation.from_dict("GET", "/users/{id}", data)
        assert all(isinstance(p, cicerone_spec.Parameter) for p in operation.parameters)
        assert operation.parameters[0].name == "id"
        assert operation.parameters[0].in_ == "path"
        assert operation.parameters[0].schema_.type == "integer"
        assert operation.parameters[1].ref == "#/components/parameters/PageSize"

    def test_security_none_means_inherit(self):
        operation = cicerone_spec.Operation.from_dict("GET", "/users", {})
        assert operation.security is None

    def test_security_empty_list_means_no_security(self):
        operation = cicerone_spec.Operation.from_dict("GET", "/health", {"security": []})
        assert operation.security == []

    def test_security_requirements(self):
        data = {"security": [{"oauth2": ["read:users"]}, {"apiKey": []}]}
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        assert operation.security == [{"oauth2": ["read:users"]}, {"apiKey": []}]

    def test_deprecated_field(self):
        operation = cicerone_spec.Operation.from_dict("GET", "/old", {"deprecated": True})
        assert operation.deprecated is True
        assert cicerone_spec.Operation.from_dict("GET", "/new", {}).deprecated is False

    def test_callbacks_typed(self):
        data = {
            "callbacks": {
                "onEvent": {
                    "{$request.body#/callbackUrl}": {
                        "post": {"responses": {"200": {"description": "OK"}}},
                    }
                }
            }
        }
        operation = cicerone_spec.Operation.from_dict("POST", "/subscribe", data)
        callback = operation.callbacks["onEvent"]
        assert isinstance(callback, cicerone_spec.Callback)
        path_item = callback.get("{$request.body#/callbackUrl}")
        assert path_item is not None
        assert "post" in path_item.operations

    def test_servers_typed(self):
        data = {"servers": [{"url": "https://api.example.com/v2"}]}
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        assert isinstance(operation.servers[0], cicerone_spec.Server)
        assert operation.servers[0].url == "https://api.example.com/v2"

    def test_external_docs_typed(self):
        data = {"externalDocs": {"url": "https://docs.example.com", "description": "More info"}}
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        assert isinstance(operation.external_docs, cicerone_spec.ExternalDocumentation)
        assert operation.external_docs.url == "https://docs.example.com"

    def test_extras_mirroring(self):
        data = {
            "requestBody": {"content": {"application/json": {"schema": {"type": "object"}}}},
            "security": [{"apiKey": []}],
            "deprecated": True,
        }
        operation = cicerone_spec.Operation.from_dict("POST", "/users", data)
        # Raw values mirrored for pre-0.4.0 consumers (removed in 0.5.0)
        assert operation.model_extra["requestBody"] == data["requestBody"]
        assert operation.model_extra["security"] == [{"apiKey": []}]
        assert operation.model_extra["deprecated"] is True


class TestMediaTypeTypedSchema:
    """MediaType.schema_ is a typed Schema, not a raw dict."""

    def test_schema_is_typed(self):
        media_type = cicerone_spec.MediaType.from_dict({"schema": {"type": "array", "items": {"type": "string"}}})
        assert isinstance(media_type.schema_, cicerone_spec.Schema)
        assert media_type.schema_.type == "array"
        assert media_type.schema_.items.type == "string"

    def test_ref_schema_is_typed(self):
        media_type = cicerone_spec.MediaType.from_dict({"schema": {"$ref": "#/components/schemas/User"}})
        assert isinstance(media_type.schema_, cicerone_spec.Schema)
        assert media_type.schema_.ref == "#/components/schemas/User"

    def test_missing_schema_is_none(self):
        media_type = cicerone_spec.MediaType.from_dict({"example": "hello"})
        assert media_type.schema_ is None


class TestParameterTypedFields:
    def test_ref_field(self):
        parameter = cicerone_spec.Parameter.from_dict({"$ref": "#/components/parameters/PageSize"})
        assert parameter.ref == "#/components/parameters/PageSize"
        assert parameter.model_extra["$ref"] == "#/components/parameters/PageSize"

    def test_deprecated_and_allow_empty_value(self):
        parameter = cicerone_spec.Parameter.from_dict(
            {"name": "q", "in": "query", "deprecated": True, "allowEmptyValue": True}
        )
        assert parameter.deprecated is True
        assert parameter.allow_empty_value is True


class TestHeaderTypedFields:
    def test_ref_and_deprecated(self):
        header = cicerone_spec.Header.from_dict({"$ref": "#/components/headers/RateLimit"})
        assert header.ref == "#/components/headers/RateLimit"
        deprecated = cicerone_spec.Header.from_dict({"description": "old", "deprecated": True})
        assert deprecated.deprecated is True


class TestRequestBodyAndResponseRef:
    def test_request_body_ref(self):
        request_body = cicerone_spec.RequestBody.from_dict({"$ref": "#/components/requestBodies/UserBody"})
        assert request_body.ref == "#/components/requestBodies/UserBody"

    def test_response_ref(self):
        response = cicerone_spec.Response.from_dict({"$ref": "#/components/responses/NotFound"})
        assert response.ref == "#/components/responses/NotFound"


class TestEncodingTypedHeaders:
    def test_headers_are_typed(self):
        encoding = cicerone_spec.Encoding.from_dict(
            {
                "contentType": "image/png",
                "headers": {"X-Rate-Limit": {"description": "limit", "schema": {"type": "integer"}}},
            }
        )
        header = encoding.headers["X-Rate-Limit"]
        assert isinstance(header, cicerone_spec.Header)
        assert header.description == "limit"
        assert header.schema_.type == "integer"


class TestLinkTypedFields:
    def test_snake_case_fields(self):
        link = cicerone_spec.Link.from_dict(
            {
                "operationId": "getUser",
                "operationRef": "#/paths/~1users~1{id}/get",
                "parameters": {"id": "$response.body#/id"},
                "server": {"url": "https://api.example.com"},
            }
        )
        assert link.operation_id == "getUser"
        assert link.operation_ref == "#/paths/~1users~1{id}/get"
        assert isinstance(link.server, cicerone_spec.Server)
        assert link.server.url == "https://api.example.com"

    def test_old_camel_case_access_still_works_via_extras(self):
        link = cicerone_spec.Link.from_dict({"operationId": "getUser"})
        # Deprecated compat: pre-0.4.0 attribute access (removed in 0.5.0)
        assert link.operationId == "getUser"


class TestPathItemTypedFields:
    def test_summary_description_and_parameters(self):
        data = {
            "summary": "User operations",
            "description": "Operations on a single user",
            "parameters": [{"name": "id", "in": "path", "required": True}],
            "get": {"operationId": "getUser"},
        }
        path_item = cicerone_spec.PathItem.from_dict("/users/{id}", data)
        assert path_item.summary == "User operations"
        assert path_item.description == "Operations on a single user"
        assert len(path_item.parameters) == 1
        assert isinstance(path_item.parameters[0], cicerone_spec.Parameter)
        assert path_item.parameters[0].name == "id"

    def test_path_level_ref(self):
        path_item = cicerone_spec.PathItem.from_dict("/users", {"$ref": "#/components/pathItems/Users"})
        assert path_item.ref == "#/components/pathItems/Users"


class TestResolverWithTypedRefs:
    """The reference resolver uses the typed ref field."""

    def test_nested_typed_refs_resolved(self):
        spec = parse_spec_from_dict(
            {
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0.0"},
                "paths": {},
                "components": {
                    "schemas": {
                        "User": {
                            "type": "object",
                            "properties": {"address": {"$ref": "#/components/schemas/Address"}},
                        },
                        "Address": {"type": "object", "properties": {"city": {"type": "string"}}},
                    }
                },
            }
        )
        user = spec.resolve_reference("#/components/schemas/User")
        assert isinstance(user, cicerone_spec.Schema)
        address = user.properties["address"]
        assert isinstance(address, cicerone_spec.Schema)
        assert address.properties["city"].type == "string"

    def test_components_schema_has_typed_ref_property(self):
        spec = parse_spec_from_dict(
            {
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0.0"},
                "paths": {},
                "components": {
                    "schemas": {
                        "Pet": {"type": "object", "properties": {"owner": {"$ref": "#/components/schemas/Owner"}}},
                        "Owner": {"type": "object"},
                    }
                },
            }
        )
        pet = spec.components.schemas["Pet"]
        assert pet.properties["owner"].ref == "#/components/schemas/Owner"


class TestEndToEndTypedParsing:
    """Full spec parse produces a fully typed tree."""

    def test_full_operation_tree_is_typed(self):
        spec = parse_spec_from_dict(
            {
                "openapi": "3.1.0",
                "info": {"title": "Test", "version": "1.0.0"},
                "paths": {
                    "/users": {
                        "post": {
                            "operationId": "createUser",
                            "deprecated": True,
                            "requestBody": {
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}
                            },
                            "responses": {"201": {"description": "Created"}},
                        }
                    }
                },
                "components": {"schemas": {"User": {"type": "object"}}},
            }
        )
        operation = spec.operation_by_operation_id("createUser")
        assert operation is not None
        assert operation.deprecated is True
        assert operation.request_body.content["application/json"].schema_.ref == "#/components/schemas/User"
        assert operation.responses["201"].description == "Created"
