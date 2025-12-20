"""Parser module for creating OpenAPISpec from various sources."""

from __future__ import annotations

import json
import pathlib
import typing
from urllib import request as urllib_request

import yaml

from cicerone.spec import components as spec_components
from cicerone.spec import info as spec_info
from cicerone.spec import model_utils
from cicerone.spec import openapi_spec as spec_openapi
from cicerone.spec import paths as spec_paths
from cicerone.spec import server as spec_server
from cicerone.spec import tag as spec_tag
from cicerone.spec import version as spec_version
from cicerone.spec import webhooks as spec_webhooks


def parse_spec_from_dict(data: typing.Mapping[str, typing.Any]) -> spec_openapi.OpenAPISpec:
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
    version = spec_version.Version(version_str)

    # Parse info
    info = model_utils.parse_nested_object(data, "info", spec_info.Info.from_dict)

    # Parse jsonSchemaDialect (OpenAPI 3.1+)
    json_schema_dialect = data.get("jsonSchemaDialect")

    # Parse paths
    paths_data = data.get("paths", {})
    paths = spec_paths.Paths.from_dict(paths_data)

    # Parse webhooks (OpenAPI 3.1+)
    webhooks = model_utils.parse_nested_object(
        data, "webhooks", spec_webhooks.Webhooks.from_dict
    ) or spec_webhooks.Webhooks(items={})

    # Parse components
    components = spec_components.Components.from_spec(data)

    # Parse servers
    servers = model_utils.parse_list(data, "servers", spec_server.Server.from_dict)

    # Parse security (top-level security requirements)
    security = data.get("security", [])

    # Parse tags
    tags = model_utils.parse_list(data, "tags", spec_tag.Tag.from_dict)

    # Parse externalDocs
    external_docs = model_utils.parse_nested_object(data, "externalDocs", spec_tag.ExternalDocumentation.from_dict)

    # Convert Mapping to dict for storage
    # This ensures we have a real dict (not just a Mapping) for the raw field
    # If data is already a dict, this is a no-op
    raw_dict = dict(data)

    return spec_openapi.OpenAPISpec(
        raw=raw_dict,
        version=version,
        info=info,
        jsonSchemaDialect=json_schema_dialect,
        servers=servers,
        paths=paths,
        webhooks=webhooks,
        components=components,
        security=security,
        tags=tags,
        externalDocs=external_docs,
    )


def parse_spec_from_json(text: str) -> spec_openapi.OpenAPISpec:
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


def parse_spec_from_yaml(text: str) -> spec_openapi.OpenAPISpec:
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


def _parse_with_format_detection(content: str, prefer_yaml: bool = False) -> spec_openapi.OpenAPISpec:
    """Parse content with automatic format detection.

    Args:
        content: The content to parse
        prefer_yaml: If True, parse as YAML. Otherwise try JSON first with YAML fallback.

    Returns:
        OpenAPISpec instance
    """
    if prefer_yaml:
        return parse_spec_from_yaml(content)
    try:
        return parse_spec_from_json(content)
    except json.JSONDecodeError:
        return parse_spec_from_yaml(content)


def parse_spec_from_file(path: str | pathlib.Path) -> spec_openapi.OpenAPISpec:
    """Create an OpenAPISpec from a file.

    Auto-detects format from file extension (.yaml/.yml for YAML, otherwise tries JSON).

    Args:
        path: Path to the OpenAPI specification file

    Returns:
        OpenAPISpec instance

    Example:
        >>> spec = parse_spec_from_file("openapi.yaml")
    """
    path_obj = pathlib.Path(path) if isinstance(path, str) else path
    content = path_obj.read_text()
    prefer_yaml = path_obj.suffix.lower() in [".yaml", ".yml"]
    return _parse_with_format_detection(content, prefer_yaml)


def parse_spec_from_url(url: str) -> spec_openapi.OpenAPISpec:
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
        prefer_yaml = "yaml" in content_type or "yml" in content_type
        return _parse_with_format_detection(content, prefer_yaml)
