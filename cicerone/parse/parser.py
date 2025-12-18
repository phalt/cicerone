"""Parser module for creating OpenAPISpec from various sources."""

import json
from pathlib import Path
from typing import Any, Mapping
from urllib import request as urllib_request

import yaml

from cicerone.spec import components
from cicerone.spec import info
from cicerone.spec import model_utils
from cicerone.spec import openapi_spec
from cicerone.spec import paths
from cicerone.spec import server
from cicerone.spec import tag
from cicerone.spec import version
from cicerone.spec import webhooks


def parse_spec_from_dict(data: Mapping[str, Any]) -> openapi_spec.OpenAPISpec:
    """Create an OpenAPISpec from a dictionary.

    Args:
        data: The OpenAPI specification as a dictionary

    Returns:
        OpenAPISpec instance

    Example:
        >>> spec_data = {"openapi": "3.0.0", "paths": {}, "info": {"title": "API"}}
        >>> spec = parse_spec_from_dict(spec_data)
    """
    # Detect version
    version_str = data.get("openapi", "3.0.0")
    version_obj = version.Version(version_str)

    # Parse info
    info_obj = model_utils.parse_nested_object(data, "info", info.Info.from_dict)

    # Parse jsonSchemaDialect (OpenAPI 3.1+)
    json_schema_dialect = data.get("jsonSchemaDialect")

    # Parse paths
    paths_data = data.get("paths", {})
    paths_obj = paths.Paths.from_dict(paths_data)

    # Parse webhooks (OpenAPI 3.1+)
    webhooks_obj = model_utils.parse_nested_object(data, "webhooks", webhooks.Webhooks.from_dict) or webhooks.Webhooks(items={})

    # Parse components
    components_obj = components.Components.from_spec(data)

    # Parse servers
    servers_list = model_utils.parse_list(data, "servers", server.Server.from_dict)

    # Parse security (top-level security requirements)
    security = data.get("security", [])

    # Parse tags
    tags_list = model_utils.parse_list(data, "tags", tag.Tag.from_dict)

    # Parse externalDocs
    external_docs = model_utils.parse_nested_object(data, "externalDocs", tag.ExternalDocumentation.from_dict)

    # Convert Mapping to dict for storage
    # This ensures we have a real dict (not just a Mapping) for the raw field
    # If data is already a dict, this is a no-op
    raw_dict = dict(data)

    return openapi_spec.OpenAPISpec(
        raw=raw_dict,
        version=version_obj,
        info=info_obj,
        jsonSchemaDialect=json_schema_dialect,
        servers=servers_list,
        paths=paths_obj,
        webhooks=webhooks_obj,
        components=components_obj,
        security=security,
        tags=tags_list,
        externalDocs=external_docs,
    )


def parse_spec_from_json(text: str) -> openapi_spec.OpenAPISpec:
    """Create an OpenAPISpec from a JSON string.

    Args:
        text: JSON string containing the OpenAPI specification

    Returns:
        OpenAPISpec instance

    Example:
        >>> json_str = '{"openapi": "3.0.0", "paths": {}, "info": {"title": "API"}}'
        >>> spec = parse_spec_from_json(json_str)
    """
    data = json.loads(text)
    return parse_spec_from_dict(data)


def parse_spec_from_yaml(text: str) -> openapi_spec.OpenAPISpec:
    """Create an OpenAPISpec from a YAML string.

    Args:
        text: YAML string containing the OpenAPI specification

    Returns:
        OpenAPISpec instance

    Example:
        >>> yaml_str = '''
        ... openapi: "3.0.0"
        ... paths: {}
        ... info:
        ...   title: API
        ... '''
        >>> spec = parse_spec_from_yaml(yaml_str)
    """
    data = yaml.safe_load(text)
    return parse_spec_from_dict(data)


def parse_spec_from_file(path: str | Path) -> openapi_spec.OpenAPISpec:
    """Create an OpenAPISpec from a file.

    Auto-detects format from file extension (.yaml/.yml for YAML, otherwise tries JSON).

    Args:
        path: Path to the OpenAPI specification file

    Returns:
        OpenAPISpec instance

    Example:
        >>> spec = parse_spec_from_file("openapi.yaml")
    """
    path_obj = Path(path) if isinstance(path, str) else path
    content = path_obj.read_text()

    # Detect format from extension
    if path_obj.suffix.lower() in [".yaml", ".yml"]:
        return parse_spec_from_yaml(content)
    else:
        # Try JSON first, fall back to YAML
        try:
            return parse_spec_from_json(content)
        except json.JSONDecodeError:
            return parse_spec_from_yaml(content)


def parse_spec_from_url(url: str) -> openapi_spec.OpenAPISpec:
    """Create an OpenAPISpec from a URL.

    Detects format from Content-Type header, defaulting to JSON with YAML fallback.

    Args:
        url: URL to fetch the OpenAPI specification from

    Returns:
        OpenAPISpec instance

    Example:
        >>> spec = parse_spec_from_url("https://api.example.com/openapi.json")
    """
    request = urllib_request.Request(url)
    with urllib_request.urlopen(request) as response:
        content = response.read().decode("utf-8")
        content_type = response.headers.get("Content-Type", "")

        # Detect format from content-type
        if "yaml" in content_type or "yml" in content_type:
            return parse_spec_from_yaml(content)
        else:
            # Try JSON first, fall back to YAML
            try:
                return parse_spec_from_json(content)
            except json.JSONDecodeError:
                return parse_spec_from_yaml(content)
