"""Tests for Callback model and callback parsing."""

from pathlib import Path
from typing import Any

import pytest

from cicerone.parse import parse_spec_from_file
from cicerone.spec.callback import Callback


class TestCallback:
    """Tests for Callback model."""

    def test_callback_from_dict(self):
        """Test creating Callback from dict."""
        data = {
            "{$request.body#/callbackUrl}": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Callback received"}
                    }
                }
            }
        }
        callback = Callback.from_dict(data)
        assert callback is not None
        assert "{$request.body#/callbackUrl}" in callback
        assert callback["{$request.body#/callbackUrl}"] is not None

    def test_callback_dict_access(self):
        """Test dict-like access to callback expressions."""
        data: dict[str, Any] = {
            "expression1": {"post": {"responses": {"200": {}}}},
            "expression2": {"get": {"responses": {"200": {}}}},
        }
        callback = Callback.from_dict(data)

        assert "expression1" in callback
        assert "expression2" in callback
        assert "expression3" not in callback

        assert callback["expression1"] is not None
        assert callback["expression2"] is not None

    def test_callback_iteration(self):
        """Test iterating over callback expressions."""
        data: dict[str, Any] = {
            "expr1": {"post": {}},
            "expr2": {"get": {}},
        }
        callback = Callback.from_dict(data)

        keys = list(callback.keys())
        assert "expr1" in keys
        assert "expr2" in keys

        values = list(callback.values())
        assert len(values) == 2


class TestCallbackParsing:
    """Tests for parsing callbacks from OpenAPI specs."""

    @pytest.fixture
    def callback_spec_path(self) -> Path:
        """Return path to callback example spec."""
        return Path(__file__).parent.parent / "fixtures" / "callback_example.yaml"

    def test_parse_spec_with_callbacks(self, callback_spec_path: Path):
        """Test parsing a spec that contains callbacks."""
        spec = parse_spec_from_file(callback_spec_path)
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0

    def test_components_callbacks_parsed(self, callback_spec_path: Path):
        """Test that callbacks in components are properly parsed."""
        spec = parse_spec_from_file(callback_spec_path)

        # Should have callbacks in components
        assert len(spec.components.callbacks) > 0
        assert "statusCallback" in spec.components.callbacks
        assert "dataCallback" in spec.components.callbacks

    def test_callback_structure(self, callback_spec_path: Path):
        """Test that callback objects have correct structure."""
        spec = parse_spec_from_file(callback_spec_path)

        # Get statusCallback
        status_callback = spec.components.callbacks["statusCallback"]
        assert status_callback is not None
        assert isinstance(status_callback, Callback)

        # Check it has expressions
        assert "{$request.body#/statusUrl}" in status_callback

        # Check we can access the path item
        path_item = status_callback["{$request.body#/statusUrl}"]
        assert path_item is not None
        assert "post" in path_item

    def test_callback_with_schema_reference(self, callback_spec_path: Path):
        """Test callback that references a schema."""
        spec = parse_spec_from_file(callback_spec_path)

        # Get dataCallback which references Event schema
        data_callback = spec.components.callbacks["dataCallback"]
        assert data_callback is not None

        # Check expression exists
        assert "{$request.body#/dataUrl}" in data_callback

        # Verify the callback structure
        path_item = data_callback["{$request.body#/dataUrl}"]
        assert "post" in path_item

    def test_all_callback_names_accessible(self, callback_spec_path: Path):
        """Test that all callback names can be retrieved."""
        spec = parse_spec_from_file(callback_spec_path)

        callback_names = list(spec.components.callbacks.keys())
        assert "statusCallback" in callback_names
        assert "dataCallback" in callback_names
        assert len(callback_names) == 2
