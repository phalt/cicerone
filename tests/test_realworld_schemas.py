"""Tests for parsing real-world OpenAPI schemas from APIs.guru openapi-directory.

These tests verify that cicerone can successfully parse large, production OpenAPI
schemas without errors. The schemas contain various OpenAPI features including:
- servers, security, securitySchemes
- component references (parameters, responses, requestBodies, examples)
- OpenAPI extensions (x-* fields)
"""

from pathlib import Path

import pytest

from cicerone.parse import parse_spec_from_file


class TestRealWorldSchemas:
    """Test parsing of real-world OpenAPI schemas from APIs.guru."""

    @pytest.fixture
    def fixtures_dir(self) -> Path:
        """Return the path to the realworld fixtures directory."""
        return Path(__file__).parent / "fixtures" / "realworld"

    def test_parse_ably_schema(self, fixtures_dir: Path) -> None:
        """Test parsing Ably.net Control API schema (OpenAPI 3.0.1)."""
        spec = parse_spec_from_file(fixtures_dir / "ably.yaml")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0
        assert spec.raw["info"]["title"] == "API V1"
        assert len(spec.paths.items) > 0
        assert len(spec.components.schemas) > 0

    def test_parse_twilio_schema(self, fixtures_dir: Path) -> None:
        """Test parsing Twilio API schema (OpenAPI 3.0.1)."""
        spec = parse_spec_from_file(fixtures_dir / "twilio.yaml")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0
        assert spec.raw["info"]["title"] == "Twilio - Api"
        assert len(spec.paths.items) > 0
        assert len(spec.components.schemas) > 0

    def test_parse_medium_schema(self, fixtures_dir: Path) -> None:
        """Test parsing Medium/Travel Partner API schema (OpenAPI 3.0.0)."""
        spec = parse_spec_from_file(fixtures_dir / "medium.yaml")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0
        assert len(spec.paths.items) > 0
        assert len(spec.components.schemas) > 0

    def test_parse_1password_schema(self, fixtures_dir: Path) -> None:
        """Test parsing 1Password Events API schema (OpenAPI 3.0.0)."""
        spec = parse_spec_from_file(fixtures_dir / "1password.yaml")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0
        assert spec.raw["info"]["title"] == "Events API"
        assert len(spec.paths.items) > 0
        assert len(spec.components.schemas) > 0

    def test_parse_google_schema(self, fixtures_dir: Path) -> None:
        """Test parsing Google Travel Partner API schema (OpenAPI 3.0.0)."""
        spec = parse_spec_from_file(fixtures_dir / "google.yaml")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0
        assert len(spec.paths.items) > 0
        assert len(spec.components.schemas) > 0

    def test_parse_spacetraders_schema(self, fixtures_dir: Path) -> None:
        """Test parsing SpaceTraders API schema (OpenAPI 3.0.0)."""
        spec = parse_spec_from_file(fixtures_dir / "spacetraders.yaml")
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0
        assert spec.raw["info"]["title"] == "SpaceTraders API"
        assert len(spec.paths.items) > 0

    def test_all_schemas_parse_without_errors(self, fixtures_dir: Path) -> None:
        """Test that all real-world schemas parse successfully."""
        schemas = [
            "ably.yaml",
            "twilio.yaml",
            "medium.yaml",
            "1password.yaml",
            "google.yaml",
            "spacetraders.yaml",
        ]

        for schema_file in schemas:
            spec = parse_spec_from_file(fixtures_dir / schema_file)
            assert spec is not None, f"Failed to parse {schema_file}"
            assert spec.version.major in (2, 3), f"Unsupported version in {schema_file}"

    def test_components_parsing(self, fixtures_dir: Path) -> None:
        """Test that component types are correctly parsed from real-world schemas."""
        # Test 1password schema which has multiple component types
        spec = parse_spec_from_file(fixtures_dir / "1password.yaml")
        # Verify various component types are present
        assert len(spec.components.schemas) > 0, "Should have schemas"
        assert len(spec.components.responses) > 0, "Should have responses"
        assert len(spec.components.requestBodies) > 0, "Should have requestBodies"
        assert len(spec.components.examples) > 0, "Should have examples"
        assert len(spec.components.securitySchemes) > 0, "Should have securitySchemes"

        # Test medium schema which has parameters
        spec = parse_spec_from_file(fixtures_dir / "medium.yaml")
        assert len(spec.components.schemas) > 0, "Should have schemas"
        assert len(spec.components.parameters) > 0, "Should have parameters"

        # Test ably schema which has securitySchemes
        spec = parse_spec_from_file(fixtures_dir / "ably.yaml")
        assert len(spec.components.schemas) > 0, "Should have schemas"
        assert len(spec.components.securitySchemes) > 0, "Should have securitySchemes"

    def test_extensions_preserved(self, fixtures_dir: Path) -> None:
        """Test that OpenAPI extensions (x-* fields) are preserved in parsed specs."""
        # Test ably schema which has multiple extensions
        spec = parse_spec_from_file(fixtures_dir / "ably.yaml")

        # Check info-level extensions
        info = spec.raw.get("info", {})
        assert "x-providerName" in info
        assert info["x-providerName"] == "ably.net"
        assert "x-serviceName" in info
        assert "x-logo" in info
        assert "x-apisguru-categories" in info
