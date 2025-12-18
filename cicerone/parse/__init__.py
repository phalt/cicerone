"""Parser utilities for OpenAPI specifications."""

from cicerone.parse import parser

__all__ = [
    "parse_spec_from_dict",
    "parse_spec_from_file",
    "parse_spec_from_json",
    "parse_spec_from_url",
    "parse_spec_from_yaml",
]

# Re-export for backward compatibility
parse_spec_from_dict = parser.parse_spec_from_dict
parse_spec_from_file = parser.parse_spec_from_file
parse_spec_from_json = parser.parse_spec_from_json
parse_spec_from_url = parser.parse_spec_from_url
parse_spec_from_yaml = parser.parse_spec_from_yaml
