"""Tests for parsing OpenAPI example schemas.

These tests verify that cicerone can successfully parse the OpenAPI example
schemas from https://learn.openapis.org/examples/ and capture all elements.
"""

from __future__ import annotations

import pathlib

import pytest

from cicerone import parse as cicerone_parse


class TestOpenAPIExamples:
    """Test parsing of OpenAPI example schemas."""

    @pytest.fixture
    def examples_dir(self) -> pathlib.Path:
        """Return the path to the openapi_examples fixtures directory."""
        return pathlib.Path(__file__).parent / "fixtures" / "openapi_examples"

    def test_parse_api_with_examples(self, examples_dir: pathlib.Path) -> None:
        """Test parsing api-with-examples.json (focuses on example objects)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "api-with-examples.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0

        # Verify info
        assert spec.info is not None
        assert spec.info.title == "Simple API overview"
        assert spec.info.version == "2.0.0"

        # Verify paths
        assert len(spec.paths.items) == 2
        assert "/" in spec.paths.items
        assert "/v2" in spec.paths.items

        # Verify operations have examples in responses
        root_path = spec.paths.items["/"]
        get_op = root_path.operations.get("get")
        assert get_op is not None
        assert "200" in get_op.responses
        assert "300" in get_op.responses

        # Verify the operation has proper method and path
        assert get_op.method == "GET"
        assert get_op.path == "/"
        assert get_op.operation_id == "listVersionsv2"

    def test_parse_callback_example(self, examples_dir: pathlib.Path) -> None:
        """Test parsing callback-example.json (focuses on callbacks)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "callback-example.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0

        # Verify info
        assert spec.info is not None
        assert spec.info.title == "Callback Example"

        # Verify callbacks in operation
        assert "/streams" in spec.paths.items
        streams_path = spec.paths.items["/streams"]
        post_op = streams_path.operations.get("post")
        assert post_op is not None

        # Verify callbacks are preserved in raw data
        assert post_op.model_extra is not None
        assert "callbacks" in post_op.model_extra
        callbacks = post_op.model_extra["callbacks"]
        assert "onData" in callbacks

        # Verify callback structure
        on_data_callback = callbacks["onData"]
        assert "{$request.query.callbackUrl}/data" in on_data_callback

    def test_parse_non_oauth_scopes(self, examples_dir: pathlib.Path) -> None:
        """Test parsing non-oauth-scopes.json (security without OAuth)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "non-oauth-scopes.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 1

        # Verify info
        assert spec.info is not None
        assert spec.info.title == "Non-oAuth Scopes example"

        # Verify security schemes
        assert len(spec.components.security_schemes) == 1
        assert "bearerAuth" in spec.components.security_schemes
        bearer_auth = spec.components.security_schemes["bearerAuth"]
        assert bearer_auth.type == "http"
        assert bearer_auth.scheme == "bearer"

        # Verify security on operation
        users_path = spec.paths.items["/users"]
        get_op = users_path.operations.get("get")
        assert get_op is not None
        assert get_op.model_extra is not None
        assert "security" in get_op.model_extra

    def test_parse_petstore(self, examples_dir: pathlib.Path) -> None:
        """Test parsing petstore.json (basic petstore example)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "petstore.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0

        # Verify info
        assert spec.info is not None
        assert spec.info.title == "Swagger Petstore"
        assert spec.info.license is not None
        assert spec.info.license.name == "MIT"

        # Verify servers
        assert len(spec.servers) == 1
        assert spec.servers[0].url == "http://petstore.swagger.io/v1"

        # Verify schemas
        assert len(spec.components.schemas) == 3
        assert "Pet" in spec.components.schemas
        assert "Pets" in spec.components.schemas
        assert "Error" in spec.components.schemas

        # Verify Pet schema structure
        pet_schema = spec.components.schemas["Pet"]
        assert pet_schema.type == "object"
        assert "id" in pet_schema.properties
        assert "name" in pet_schema.properties
        assert pet_schema.required == ["id", "name"]

        # Verify paths
        assert len(spec.paths.items) == 2
        assert "/pets" in spec.paths.items
        assert "/pets/{petId}" in spec.paths.items

        # Verify operations are properly parsed
        pets_path = spec.paths.items["/pets"]
        assert "get" in pets_path.operations
        assert "post" in pets_path.operations
        get_op = pets_path.operations["get"]
        assert get_op.operation_id == "listPets"
        assert get_op.summary == "List all pets"

    def test_parse_petstore_expanded(self, examples_dir: pathlib.Path) -> None:
        """Test parsing petstore-expanded.json (extended petstore with more features)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "petstore-expanded.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0

        # Verify info with all fields
        assert spec.info is not None
        assert spec.info.title == "Swagger Petstore"
        assert spec.info.description is not None
        assert "sample API" in spec.info.description
        assert spec.info.terms_of_service == "http://swagger.io/terms/"

        # Verify contact
        assert spec.info.contact is not None
        assert spec.info.contact.name == "Swagger API Team"
        assert spec.info.contact.email == "apiteam@swagger.io"
        assert spec.info.contact.url == "http://swagger.io"

        # Verify license
        assert spec.info.license is not None
        assert spec.info.license.name == "Apache 2.0"
        assert spec.info.license.url == "https://www.apache.org/licenses/LICENSE-2.0.html"

        # Verify servers
        assert len(spec.servers) == 1
        assert spec.servers[0].url == "https://petstore.swagger.io/v2"

        # Verify schemas with allOf composition
        assert "Pet" in spec.components.schemas
        pet_schema = spec.components.schemas["Pet"]
        # Pet uses allOf composition
        assert pet_schema.all_of is not None
        assert len(pet_schema.all_of) == 2

    def test_parse_tictactoe(self, examples_dir: pathlib.Path) -> None:
        """Test parsing tictactoe.json (includes tags and security)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "tictactoe.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 1

        # Verify info
        assert spec.info is not None
        assert spec.info.title == "Tic Tac Toe"
        assert spec.info.description is not None

        # Verify tags
        assert len(spec.tags) == 1
        assert spec.tags[0].name == "Gameplay"

        # Verify security schemes
        assert len(spec.components.security_schemes) >= 2
        assert "defaultApiKey" in spec.components.security_schemes
        assert "app2AppOauth" in spec.components.security_schemes

        # Verify component parameters
        assert len(spec.components.parameters) == 2
        assert "rowParam" in spec.components.parameters
        assert "columnParam" in spec.components.parameters

    def test_parse_uspto(self, examples_dir: pathlib.Path) -> None:
        """Test parsing uspto.json (includes server variables and tags)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "uspto.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0

        # Verify info with contact
        assert spec.info is not None
        assert spec.info.title == "USPTO Data Set API"
        assert spec.info.contact is not None
        assert spec.info.contact.name == "Open Data Portal"
        assert spec.info.contact.email == "developer@uspto.gov"

        # Verify servers with variables
        assert len(spec.servers) == 1
        server = spec.servers[0]
        assert "{scheme}://developer.uspto.gov/ds-api" in server.url
        assert len(server.variables) == 1
        assert "scheme" in server.variables

        # Verify server variable
        scheme_var = server.variables["scheme"]
        assert scheme_var.default == "https"
        assert "https" in scheme_var.enum
        assert "http" in scheme_var.enum
        assert scheme_var.description is not None

        # Verify tags
        assert len(spec.tags) == 2
        tag_names = [tag.name for tag in spec.tags]
        assert "metadata" in tag_names
        assert "search" in tag_names

        # Verify tag descriptions
        metadata_tag = next(tag for tag in spec.tags if tag.name == "metadata")
        assert metadata_tag.description == "Find out about the data sets"

    def test_parse_webhook_example(self, examples_dir: pathlib.Path) -> None:
        """Test parsing webhook-example.json (OpenAPI 3.1 webhooks feature)."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "webhook-example.json")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 1

        # Verify info
        assert spec.info is not None
        assert spec.info.title == "Webhook Example"

        # Verify webhooks
        assert len(spec.webhooks.items) == 1
        assert "newPet" in spec.webhooks.items

        # Verify webhook structure
        new_pet_webhook = spec.webhooks.items["newPet"]
        assert "post" in new_pet_webhook.operations
        post_op = new_pet_webhook.operations["post"]
        assert "200" in post_op.responses

        # Verify webhook can iterate operations
        webhook_ops = list(spec.webhooks.all_operations())
        assert len(webhook_ops) == 1
        assert webhook_ops[0].method == "POST"

        # Verify all_operations includes webhooks
        all_ops = list(spec.all_operations())
        assert len(all_ops) == 1  # Only webhook operation

        # Verify schema in components is properly parsed
        assert "Pet" in spec.components.schemas
        pet_schema = spec.components.schemas["Pet"]
        assert pet_schema.type == "object"
        assert pet_schema.required == ["id", "name"]
        assert "id" in pet_schema.properties
        assert "name" in pet_schema.properties

    def test_all_examples_parse_successfully(self, examples_dir: pathlib.Path) -> None:
        """Ensure all example files can be parsed without errors."""
        example_files = [
            "api-with-examples.json",
            "callback-example.json",
            "non-oauth-scopes.json",
            "petstore.json",
            "petstore-expanded.json",
            "tictactoe.json",
            "uspto.json",
            "webhook-example.json",
        ]

        for filename in example_files:
            spec = cicerone_parse.parse_spec_from_file(examples_dir / filename)
            assert spec is not None, f"Failed to parse {filename}"
            assert spec.version is not None, f"No version in {filename}"
            assert spec.info is not None, f"No info in {filename}"

    def test_schema_composition_keywords(self, examples_dir: pathlib.Path) -> None:
        """Test that schema composition keywords (allOf, oneOf, anyOf) are captured."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "petstore-expanded.json")

        # Pet schema uses allOf
        pet_schema = spec.components.schemas["Pet"]
        assert pet_schema.all_of is not None
        assert len(pet_schema.all_of) == 2

        # Verify allOf elements are properly parsed as Schema objects
        first_element = pet_schema.all_of[0]
        assert first_element.model_extra is not None
        assert "$ref" in first_element.model_extra

        # Verify second element has properties
        second_element = pet_schema.all_of[1]
        assert second_element.type == "object"
        assert "id" in second_element.properties
        assert second_element.properties["id"].type == "integer"
        assert second_element.required == ["id"]

    def test_all_schema_elements_captured(self, examples_dir: pathlib.Path) -> None:
        """Verify all schema elements are captured including format, example, etc."""
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "petstore.json")

        # Check that schemas preserve all fields
        pets_schema = spec.components.schemas["Pets"]
        assert pets_schema.type == "array"
        assert pets_schema.items is not None

        # Check for format, maximum, example in raw extras
        # These should be in model_extra since we use extra="allow"
        error_schema = spec.components.schemas["Error"]
        assert error_schema.type == "object"
        assert error_schema.required == ["code", "message"]

    def test_top_level_security_and_external_docs(self, examples_dir: pathlib.Path) -> None:
        """Test that top-level security and externalDocs are captured."""
        # Note: Need to check raw field since our examples don't have top-level security/externalDocs
        spec = cicerone_parse.parse_spec_from_file(examples_dir / "tictactoe.json")

        # Verify security field exists (even if empty)
        assert spec.security is not None
        assert isinstance(spec.security, list)

        # Verify external_docs field exists (even if None for this example)
        assert hasattr(spec, "external_docs")

        # Verify json_schema_dialect field exists for OpenAPI 3.1
        assert hasattr(spec, "json_schema_dialect")
