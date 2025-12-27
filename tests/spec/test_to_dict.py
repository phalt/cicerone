"""Tests for to_dict() methods on spec models.

These tests ensure that models can be round-tripped (dict -> model -> dict)
and that the to_dict() methods properly handle all fields including Pydantic
extra fields like $ref, enum, format, nullable, etc.
"""

from __future__ import annotations

from cicerone import spec as cicerone_spec


class TestSchemaToDict:
    """Tests for Schema.to_dict() method."""

    def test_basic_schema_to_dict(self):
        """Test converting a basic schema to dict."""
        data = {
            "type": "object",
            "title": "User",
            "description": "A user object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result["type"] == "object"
        assert result["title"] == "User"
        assert result["description"] == "A user object"
        assert result["required"] == ["id", "name"]
        assert "id" in result["properties"]
        assert result["properties"]["id"]["type"] == "string"
        assert result["properties"]["name"]["type"] == "string"
        assert result["properties"]["age"]["type"] == "integer"

    def test_schema_with_ref_to_dict(self):
        """Test that $ref schemas return early with only $ref field."""
        data = {"$ref": "#/components/schemas/User"}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result == {"$ref": "#/components/schemas/User"}
        # No other fields should be present when $ref is set
        assert len(result) == 1

    def test_schema_with_enum_to_dict(self):
        """Test schema with enum in extra fields."""
        data = {"type": "string", "enum": ["read", "write", "admin"]}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result["type"] == "string"
        assert result["enum"] == ["read", "write", "admin"]

    def test_schema_with_format_to_dict(self):
        """Test schema with format in extra fields."""
        data = {"type": "string", "format": "date-time"}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result["type"] == "string"
        assert result["format"] == "date-time"

    def test_schema_with_nullable_to_dict(self):
        """Test schema with nullable in extra fields."""
        data = {"type": "string", "nullable": True}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result["type"] == "string"
        assert result["nullable"] is True

    def test_schema_with_array_type_to_dict(self):
        """Test schema with type as array (OpenAPI 3.1)."""
        data = {"type": ["string", "null"]}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result["type"] == ["string", "null"]

    def test_nested_schema_to_dict(self):
        """Test schema with nested objects."""
        data = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
            },
        }
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result["type"] == "object"
        assert "user" in result["properties"]
        assert result["properties"]["user"]["type"] == "object"
        assert "name" in result["properties"]["user"]["properties"]

    def test_array_schema_to_dict(self):
        """Test schema with array items."""
        data = {"type": "array", "items": {"type": "string"}}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert result["type"] == "array"
        assert result["items"]["type"] == "string"

    def test_schema_with_allof_to_dict(self):
        """Test schema with allOf composition."""
        data = {
            "allOf": [
                {"$ref": "#/components/schemas/Base"},
                {"type": "object", "properties": {"extra": {"type": "string"}}},
            ]
        }
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert "allOf" in result
        assert len(result["allOf"]) == 2
        assert result["allOf"][0]["$ref"] == "#/components/schemas/Base"
        assert result["allOf"][1]["type"] == "object"

    def test_schema_with_oneof_to_dict(self):
        """Test schema with oneOf composition."""
        data = {
            "oneOf": [
                {"type": "string"},
                {"type": "integer"},
            ]
        }
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert "oneOf" in result
        assert len(result["oneOf"]) == 2

    def test_schema_with_anyof_to_dict(self):
        """Test schema with anyOf composition."""
        data = {
            "anyOf": [
                {"type": "string"},
                {"type": "null"},
            ]
        }
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert "anyOf" in result
        assert len(result["anyOf"]) == 2

    def test_schema_with_not_to_dict(self):
        """Test schema with not composition."""
        data = {"not": {"type": "string"}}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        assert "not" in result
        assert result["not"]["type"] == "string"

    def test_empty_schema_to_dict(self):
        """Test converting an empty schema to dict."""
        data: dict[str, str] = {}
        schema = cicerone_spec.Schema.from_dict(data)
        result = schema.to_dict()

        # Empty schema should return empty dict
        assert result == {}


class TestParameterToDict:
    """Tests for Parameter.to_dict() method."""

    def test_basic_parameter_to_dict(self):
        """Test converting a basic parameter to dict."""
        data = {
            "name": "userId",
            "in": "path",
            "required": True,
            "schema": {"type": "string"},
        }
        param = cicerone_spec.Parameter.from_dict(data)
        result = param.to_dict()

        assert result["name"] == "userId"
        assert result["in"] == "path"
        assert result["required"] is True
        assert result["schema"]["type"] == "string"

    def test_parameter_with_ref_to_dict(self):
        """Test parameter with $ref."""
        data = {"$ref": "#/components/parameters/UserId"}
        param = cicerone_spec.Parameter.from_dict(data)
        result = param.to_dict()

        assert result == {"$ref": "#/components/parameters/UserId"}

    def test_parameter_with_description_to_dict(self):
        """Test parameter with description."""
        data = {
            "name": "limit",
            "in": "query",
            "description": "Maximum number of items to return",
            "schema": {"type": "integer"},
        }
        param = cicerone_spec.Parameter.from_dict(data)
        result = param.to_dict()

        assert result["description"] == "Maximum number of items to return"


class TestRequestBodyToDict:
    """Tests for RequestBody.to_dict() method."""

    def test_basic_request_body_to_dict(self):
        """Test converting a basic request body to dict."""
        data = {
            "description": "User to create",
            "required": True,
            "content": {"application/json": {"schema": {"type": "object", "properties": {"name": {"type": "string"}}}}},
        }
        req_body = cicerone_spec.RequestBody.from_dict(data)
        result = req_body.to_dict()

        assert result["description"] == "User to create"
        assert result["required"] is True
        assert "application/json" in result["content"]
        assert result["content"]["application/json"]["schema"]["type"] == "object"


class TestResponseToDict:
    """Tests for Response.to_dict() method."""

    def test_basic_response_to_dict(self):
        """Test converting a basic response to dict."""
        data = {
            "description": "Successful response",
            "content": {"application/json": {"schema": {"type": "object", "properties": {"id": {"type": "string"}}}}},
        }
        response = cicerone_spec.Response.from_dict(data)
        result = response.to_dict()

        assert result["description"] == "Successful response"
        assert "application/json" in result["content"]
        assert result["content"]["application/json"]["schema"]["type"] == "object"


class TestOperationToDict:
    """Tests for Operation.to_dict() method."""

    def test_basic_operation_to_dict(self):
        """Test converting a basic operation to dict."""
        data = {
            "operationId": "listUsers",
            "summary": "List users",
            "description": "Get all users",
            "tags": ["users"],
            "parameters": [{"name": "limit", "in": "query", "schema": {"type": "integer"}}],
            "responses": {"200": {"description": "OK"}},
        }
        operation = cicerone_spec.Operation.from_dict("GET", "/users", data)
        result = operation.to_dict()

        assert result["operationId"] == "listUsers"
        assert result["summary"] == "List users"
        assert result["description"] == "Get all users"
        assert result["tags"] == ["users"]
        assert len(result["parameters"]) == 1
        assert "200" in result["responses"]

    def test_operation_with_deprecated_to_dict(self):
        """Test operation with deprecated flag in extra fields."""
        data = {
            "operationId": "oldMethod",
            "deprecated": True,
            "responses": {"200": {"description": "OK"}},
        }
        operation = cicerone_spec.Operation.from_dict("GET", "/old", data)
        result = operation.to_dict()

        assert result["operationId"] == "oldMethod"
        assert result["deprecated"] is True


class TestPathItemToDict:
    """Tests for PathItem.to_dict() method."""

    def test_basic_path_item_to_dict(self):
        """Test converting a basic path item to dict."""
        data = {
            "get": {
                "operationId": "getUser",
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "operationId": "createUser",
                "responses": {"201": {"description": "Created"}},
            },
        }
        path_item = cicerone_spec.PathItem.from_dict("/users", data)
        result = path_item.to_dict()

        assert "get" in result
        assert result["get"]["operationId"] == "getUser"
        assert "post" in result
        assert result["post"]["operationId"] == "createUser"

    def test_path_item_with_parameters_to_dict(self):
        """Test path item with path-level parameters."""
        data = {
            "parameters": [{"name": "userId", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {
                "operationId": "getUser",
                "responses": {"200": {"description": "OK"}},
            },
        }
        path_item = cicerone_spec.PathItem.from_dict("/users/{userId}", data)
        result = path_item.to_dict()

        assert "parameters" in result
        assert len(result["parameters"]) == 1
        assert result["parameters"][0]["name"] == "userId"


class TestMediaTypeToDict:
    """Tests for MediaType.to_dict() method."""

    def test_basic_media_type_to_dict(self):
        """Test converting a basic media type to dict."""
        data = {
            "schema": {"type": "object", "properties": {"id": {"type": "string"}}},
            "example": {"id": "123"},
        }
        media_type = cicerone_spec.MediaType.from_dict(data)
        result = media_type.to_dict()

        assert result["schema"]["type"] == "object"
        assert result["example"]["id"] == "123"


class TestExampleToDict:
    """Tests for Example.to_dict() method."""

    def test_basic_example_to_dict(self):
        """Test converting a basic example to dict."""
        data = {
            "summary": "Example user",
            "value": {"id": "123", "name": "John"},
        }
        example = cicerone_spec.Example.from_dict(data)
        result = example.to_dict()

        assert result["summary"] == "Example user"
        assert result["value"]["id"] == "123"


class TestHeaderToDict:
    """Tests for Header.to_dict() method."""

    def test_basic_header_to_dict(self):
        """Test converting a basic header to dict."""
        data = {
            "description": "Rate limit",
            "schema": {"type": "integer"},
        }
        header = cicerone_spec.Header.from_dict(data)
        result = header.to_dict()

        assert result["description"] == "Rate limit"
        assert result["schema"]["type"] == "integer"


class TestLinkToDict:
    """Tests for Link.to_dict() method."""

    def test_basic_link_to_dict(self):
        """Test converting a basic link to dict."""
        data = {
            "operationId": "getUserById",
            "parameters": {"userId": "$response.body#/id"},
        }
        link = cicerone_spec.Link.from_dict(data)
        result = link.to_dict()

        assert result["operationId"] == "getUserById"
        assert result["parameters"]["userId"] == "$response.body#/id"


class TestEncodingToDict:
    """Tests for Encoding.to_dict() method."""

    def test_basic_encoding_to_dict(self):
        """Test converting a basic encoding to dict."""
        data = {
            "contentType": "application/xml; charset=utf-8",
            "style": "form",
        }
        encoding = cicerone_spec.Encoding.from_dict(data)
        result = encoding.to_dict()

        assert result["contentType"] == "application/xml; charset=utf-8"
        assert result["style"] == "form"
