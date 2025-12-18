"""Tests for Webhooks model."""

from typing import Any

from cicerone.spec import (
    Webhooks,
)


class TestWebhooks:
    """Tests for Webhooks model."""

    def test_webhooks_from_dict(self):
        """Test creating Webhooks from dict."""
        data = {
            "newPet": {
                "post": {
                    "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Pet"}}}},
                    "responses": {"200": {"description": "OK"}},
                }
            }
        }
        webhooks = Webhooks.from_dict(data)
        assert "newPet" in webhooks.items
        assert "post" in webhooks.items["newPet"].operations

    def test_webhooks_empty(self):
        """Test creating empty Webhooks."""
        webhooks = Webhooks.from_dict({})
        assert len(webhooks.items) == 0

    def test_webhooks_all_operations(self):
        """Test getting all operations from webhooks."""
        data: dict[str, Any] = {
            "webhook1": {
                "post": {"responses": {"200": {}}},
            },
            "webhook2": {
                "get": {"responses": {"200": {}}},
                "post": {"responses": {"200": {}}},
            },
        }
        webhooks = Webhooks.from_dict(data)
        operations = list(webhooks.all_operations())
        assert len(operations) == 3
        methods = [op.method for op in operations]
        assert "POST" in methods
        assert "GET" in methods

    def test_webhooks_str_representation_empty(self):
        """Test __str__ method for empty webhooks."""
        webhooks = Webhooks.from_dict({})
        str_repr = str(webhooks)
        assert "<Webhooks: empty>" in str_repr

    def test_webhooks_str_representation_single(self):
        """Test __str__ method with single webhook."""
        data: dict[str, Any] = {
            "newPet": {
                "post": {"responses": {"200": {}}},
            }
        }
        webhooks = Webhooks.from_dict(data)
        str_repr = str(webhooks)
        assert "<Webhooks:" in str_repr
        assert "1 webhooks" in str_repr
        assert "newPet" in str_repr

    def test_webhooks_str_representation_multiple(self):
        """Test __str__ method with multiple webhooks."""
        data: dict[str, Any] = {
            "webhook1": {"post": {"responses": {"200": {}}}},
            "webhook2": {"post": {"responses": {"200": {}}}},
            "webhook3": {"post": {"responses": {"200": {}}}},
            "webhook4": {"post": {"responses": {"200": {}}}},
        }
        webhooks = Webhooks.from_dict(data)
        str_repr = str(webhooks)
        assert "4 webhooks" in str_repr
        # Should show first 3 and indicate more
        assert "(+1 more)" in str_repr
