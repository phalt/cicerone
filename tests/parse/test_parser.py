"""Tests for parser module."""

from __future__ import annotations

import json
import pathlib
from unittest import mock

from cicerone import parse as cicerone_parse


class TestParser:
    """Tests for parser functions."""

    def test_parse_from_dict(self):
        """Test parsing from dictionary."""
        data = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        spec = cicerone_parse.parse_spec_from_dict(data)
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
        spec = cicerone_parse.parse_spec_from_json(json_str)
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
        spec = cicerone_parse.parse_spec_from_yaml(yaml_str)
        assert spec.version.major == 3

    def test_parse_from_file_yaml(self):
        """Test parsing YAML file."""
        fixture_path = pathlib.Path(__file__).parent.parent / "fixtures" / "petstore_openapi3.yaml"
        spec = cicerone_parse.parse_spec_from_file(fixture_path)
        assert spec.version.major == 3
        assert "/users" in spec.paths

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
        mock_response = mock.Mock()
        mock_response.read.return_value = json.dumps(json_spec).encode("utf-8")
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.__enter__ = mock.Mock(return_value=mock_response)
        mock_response.__exit__ = mock.Mock(return_value=False)
        with mock.patch("cicerone.parse.parser.urllib_request.urlopen", return_value=mock_response):
            spec = cicerone_parse.parse_spec_from_url("https://example.com/openapi.json")
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
        mock_response = mock.Mock()
        mock_response.read.return_value = yaml_spec.encode("utf-8")
        mock_response.headers = {"Content-Type": "application/yaml"}
        mock_response.__enter__ = mock.Mock(return_value=mock_response)
        mock_response.__exit__ = mock.Mock(return_value=False)
        with mock.patch("cicerone.parse.parser.urllib_request.urlopen", return_value=mock_response):
            spec = cicerone_parse.parse_spec_from_url("https://example.com/openapi.json")
            assert spec.version.major == 3
            assert "/test" in spec.paths

    def test_parse_from_file_json_fallback_to_yaml(self, tmp_path):
        """Test parsing a file with .json extension but YAML content (fallback)."""
        yaml_content = """
openapi: "3.0.0"
info:
  title: Test
  version: "1.0.0"
paths: {}
"""
        file_path = tmp_path / "spec.json"
        file_path.write_text(yaml_content)

        spec = cicerone_parse.parse_spec_from_file(file_path)
        assert spec.version.major == 3

    def test_parse_from_url_json_fallback_to_yaml(self):
        """Test parsing URL with JSON content-type but YAML content (fallback)."""
        yaml_content = """
openapi: "3.0.0"
info:
  title: Test
  version: "1.0.0"
paths:
  /test:
    get:
      operationId: getTest
"""
        # Mock with JSON content-type but YAML content
        mock_response = mock.Mock()
        mock_response.read.return_value = yaml_content.encode("utf-8")
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.__enter__ = mock.Mock(return_value=mock_response)
        mock_response.__exit__ = mock.Mock(return_value=False)
        with mock.patch("cicerone.parse.parser.urllib_request.urlopen", return_value=mock_response):
            spec = cicerone_parse.parse_spec_from_url("https://example.com/openapi.json")
            assert spec.version.major == 3
            assert "/test" in spec.paths
