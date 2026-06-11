"""Tests for the Discriminator model.

References:
- OpenAPI 3.x Discriminator Object: https://spec.openapis.org/oas/v3.1.0#discriminator-object
"""

from __future__ import annotations

from cicerone import spec as cicerone_spec
from cicerone.parse import parse_spec_from_dict


class TestDiscriminator:
    def test_from_dict_with_property_name(self):
        discriminator = cicerone_spec.Discriminator.from_dict({"propertyName": "petType"})
        assert discriminator.property_name == "petType"
        assert discriminator.mapping == {}

    def test_from_dict_with_mapping(self):
        discriminator = cicerone_spec.Discriminator.from_dict(
            {
                "propertyName": "petType",
                "mapping": {
                    "dog": "#/components/schemas/Dog",
                    "cat": "#/components/schemas/Cat",
                },
            }
        )
        assert discriminator.property_name == "petType"
        assert discriminator.mapping["dog"] == "#/components/schemas/Dog"
        assert discriminator.mapping["cat"] == "#/components/schemas/Cat"

    def test_str_representation(self):
        discriminator = cicerone_spec.Discriminator.from_dict(
            {"propertyName": "petType", "mapping": {"dog": "#/components/schemas/Dog"}}
        )
        text = str(discriminator)
        assert "petType" in text
        assert "1 mapping" in text


class TestSchemaDiscriminator:
    def test_schema_discriminator_is_typed(self):
        schema = cicerone_spec.Schema.from_dict(
            {
                "oneOf": [{"$ref": "#/components/schemas/Dog"}, {"$ref": "#/components/schemas/Cat"}],
                "discriminator": {"propertyName": "petType"},
            }
        )
        assert isinstance(schema.discriminator, cicerone_spec.Discriminator)
        assert schema.discriminator.property_name == "petType"
        assert schema.one_of is not None
        assert schema.one_of[0].ref == "#/components/schemas/Dog"

    def test_schema_without_discriminator(self):
        schema = cicerone_spec.Schema.from_dict({"type": "object"})
        assert schema.discriminator is None

    def test_discriminator_in_parsed_spec(self):
        spec = parse_spec_from_dict(
            {
                "openapi": "3.0.0",
                "info": {"title": "Pets", "version": "1.0.0"},
                "paths": {},
                "components": {
                    "schemas": {
                        "Pet": {
                            "oneOf": [
                                {"$ref": "#/components/schemas/Dog"},
                                {"$ref": "#/components/schemas/Cat"},
                            ],
                            "discriminator": {
                                "propertyName": "petType",
                                "mapping": {"dog": "#/components/schemas/Dog"},
                            },
                        },
                        "Dog": {"type": "object", "properties": {"petType": {"type": "string"}}},
                        "Cat": {"type": "object", "properties": {"petType": {"type": "string"}}},
                    }
                },
            }
        )
        pet = spec.components.schemas["Pet"]
        assert pet.discriminator.property_name == "petType"
        assert pet.discriminator.mapping == {"dog": "#/components/schemas/Dog"}
