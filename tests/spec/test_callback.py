"""Tests for Callback model and callback parsing."""

from __future__ import annotations

import pathlib
import typing

import pytest

from cicerone import parse as cicerone_parse
from cicerone import spec as cicerone_spec


class TestCallback:
    """Tests for Callback model."""

    def test_callback_from_dict(self):
        """Test creating Callback from dict."""
        data: dict[str, typing.Any] = {
            "{$request.body#/callbackUrl}": {
                "post": {
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object"}}}},
                    "responses": {"200": {"description": "Callback received"}},
                }
            }
        }
        callback = cicerone_spec.Callback.from_dict(data)
        assert callback is not None
        assert callback.get("{$request.body#/callbackUrl}") is not None

    def test_callback_get_method(self):
        """Test get method for accessing expressions."""
        data: dict[str, typing.Any] = {
            "expression1": {"post": {"responses": {"200": {}}}},
            "expression2": {"get": {"responses": {"200": {}}}},
        }
        callback = cicerone_spec.Callback.from_dict(data)

        assert callback.get("expression1") is not None
        assert callback.get("expression2") is not None
        assert callback.get("expression3") is None

    def test_callback_expressions_access(self):
        """Test direct access to expressions dict."""
        data: dict[str, typing.Any] = {
            "expr1": {"post": {}},
            "expr2": {"get": {}},
        }
        callback = cicerone_spec.Callback.from_dict(data)

        assert len(callback.expressions) == 2
        assert "expr1" in callback.expressions
        assert "expr2" in callback.expressions


class TestCallbackParsing:
    """Tests for parsing callbacks from OpenAPI specs."""

    @pytest.fixture
    def callback_spec_path(self) -> pathlib.Path:
        """Return path to callback example spec."""
        return pathlib.Path(__file__).parent.parent / "fixtures" / "callback_example.yaml"

    def test_parse_spec_with_callbacks(self, callback_spec_path: pathlib.Path):
        """Test parsing a spec that contains callbacks."""
        spec = cicerone_parse.parse_spec_from_file(callback_spec_path)
        assert spec is not None
        assert spec.version.major == 3
        assert spec.version.minor == 0

    def test_operation_callbacks_parsed(self, callback_spec_path: pathlib.Path):
        """Test that callbacks in operations are accessible."""
        spec = cicerone_parse.parse_spec_from_file(callback_spec_path)

        # The /streams POST operation has a callback
        streams_path = spec.paths["/streams"]
        assert streams_path is not None

        post_op = streams_path.operations.get("post")
        assert post_op is not None

    def test_callback_expression_structure(self, callback_spec_path: pathlib.Path):
        """Test that callback objects have correct structure."""
        spec = cicerone_parse.parse_spec_from_file(callback_spec_path)

        # Access the raw callbacks from the operation
        streams_path = spec.raw["paths"]["/streams"]
        post_op = streams_path["post"]
        assert "callbacks" in post_op

        callbacks = post_op["callbacks"]
        assert "onData" in callbacks

        # Parse the onData callback
        on_data_callback = cicerone_spec.Callback.from_dict(callbacks["onData"])
        assert on_data_callback is not None

        # Check it has the expression
        expression = "{$request.query.callbackUrl}/data"
        path_item = on_data_callback.get(expression)
        assert path_item is not None
        assert "post" in path_item.operations
