"""Tests for parser module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

from cicerone.parse import (
    parse_spec_from_dict,
    parse_spec_from_file,
    parse_spec_from_json,
    parse_spec_from_url,
    parse_spec_from_yaml,
)


class TestParser:
    """Tests for parser functions."""

    def test_parse_from_dict(self):
        """Test parsing from dictionary."""
        data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        spec = parse_spec_from_dict(data)
        assert spec.version.major == 3

    def test_parse_from_json(self):
        """Test parsing from JSON string."""
        json_str = json.dumps(
            {
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0.0"},
                "paths": {},
            }
        )
        spec = parse_spec_from_json(json_str)
        assert spec.version.major == 3

    def test_parse_from_yaml(self):
        """Test parsing from YAML string."""
        yaml_str = """
openapi: "3.0.0"
info:
  title: Test
  version: "1.0.0"
paths: {}
"""
        spec = parse_spec_from_yaml(yaml_str)
        assert spec.version.major == 3

    def test_parse_from_file_yaml(self):
        """Test parsing YAML file."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "petstore_openapi3.yaml"
        spec = parse_spec_from_file(fixture_path)
        assert spec.version.major == 3
        assert "/users" in spec.paths

    def test_parse_from_file_swagger2(self):
        """Test parsing Swagger 2.0 file."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "swagger2.yaml"
        spec = parse_spec_from_file(fixture_path)
        assert spec.version.major == 2

    def test_parse_from_url_json(self):
        """Test loading spec from URL with JSON content."""
        json_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {"operationId": "getTest"},
                },
            },
        }

        # Mock the urlopen call
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(json_spec).encode("utf-8")
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch("cicerone.parse.parser.urlopen", return_value=mock_response):
            spec = parse_spec_from_url("https://example.com/openapi.json")
            assert spec.version.major == 3
            assert "/test" in spec.paths

    def test_parse_from_url_yaml(self):
        """Test loading spec from URL with YAML content."""
        yaml_spec = """
openapi: "3.0.0"
info:
  title: Test
  version: "1.0.0"
paths:
  /test:
    get:
      operationId: getTest
"""

        # Mock the urlopen call
        mock_response = Mock()
        mock_response.read.return_value = yaml_spec.encode("utf-8")
        mock_response.headers = {"Content-Type": "application/yaml"}
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch("cicerone.parse.parser.urlopen", return_value=mock_response):
            spec = parse_spec_from_url("https://example.com/openapi.yaml")
            assert spec.version.major == 3
            assert "/test" in spec.paths
