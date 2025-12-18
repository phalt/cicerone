"""Parser module for creating OpenAPISpec from various sources."""

import json
from pathlib import Path
from typing import Any, Mapping
from urllib.request import Request, urlopen

import yaml

from cicerone.spec.components import Components
from cicerone.spec.info import Info
from cicerone.spec.openapi_spec import OpenAPISpec
from cicerone.spec.paths import Paths
from cicerone.spec.server import Server
from cicerone.spec.tag import Tag
from cicerone.spec.version import Version
from cicerone.spec.webhooks import Webhooks


def parse_spec_from_dict(data: Mapping[str, Any]) -> OpenAPISpec:
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
    version = Version(version_str)

    # Parse info
    info = None
    if "info" in data:
        info = Info.from_dict(data["info"])

    # Parse paths
    paths_data = data.get("paths", {})
    paths = Paths.from_dict(paths_data)

    # Parse webhooks (OpenAPI 3.1+)
    webhooks = Webhooks(items={})
    if "webhooks" in data:
        webhooks = Webhooks.from_dict(data["webhooks"])

    # Parse components
    components = Components.from_spec(data)

    # Parse servers
    servers = []
    if "servers" in data and isinstance(data["servers"], list):
        servers = [Server.from_dict(server_data) for server_data in data["servers"]]

    # Parse tags
    tags = []
    if "tags" in data and isinstance(data["tags"], list):
        tags = [Tag.from_dict(tag_data) for tag_data in data["tags"]]

    # Convert Mapping to dict for storage
    # This ensures we have a real dict (not just a Mapping) for the raw field
    # If data is already a dict, this is a no-op
    raw_dict = dict(data)

    return OpenAPISpec(
        raw=raw_dict,
        version=version,
        info=info,
        paths=paths,
        webhooks=webhooks,
        components=components,
        servers=servers,
        tags=tags,
    )


def parse_spec_from_json(text: str) -> OpenAPISpec:
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


def parse_spec_from_yaml(text: str) -> OpenAPISpec:
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


def parse_spec_from_file(path: str | Path) -> OpenAPISpec:
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


def parse_spec_from_url(url: str) -> OpenAPISpec:
    """Create an OpenAPISpec from a URL.

    Detects format from Content-Type header, defaulting to JSON with YAML fallback.

    Args:
        url: URL to fetch the OpenAPI specification from

    Returns:
        OpenAPISpec instance

    Example:
        >>> spec = parse_spec_from_url("https://api.example.com/openapi.json")
    """
    request = Request(url)
    with urlopen(request) as response:
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
