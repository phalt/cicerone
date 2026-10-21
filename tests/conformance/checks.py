"""The two conformance checks, shared by the tests and the allowlist generator."""

from __future__ import annotations

import json
import tomllib
import typing

import yaml

import cicerone

from . import models, oai_tables

ALLOWLIST = oai_tables.FIXTURES / "allowlist.toml"

# Allowlist entries that can never pass, as opposed to gaps a task will close
PERMANENT_PREFIXES = ("by design:", "erratum:")


def allowlist(section: typing.Literal["fields", "examples"]) -> dict[str, str]:
    """Known gaps for one check, mapped to the reason each is allowed."""
    with ALLOWLIST.open("rb") as handle:
        return tomllib.load(handle).get(section, {})


def field_gaps() -> dict[str, str]:
    """Fixed fields cicerone does not type yet, keyed ``version/Object/field``, valued by object."""
    gaps: dict[str, str] = {}
    for version in oai_tables.FIELD_SOURCES:
        for field in oai_tables.fixed_fields(version):
            if not models.is_field_covered(field.object_name, field.field):
                gaps[f"{version}/{field.object_name}/{field.field}"] = field.object_name
    return gaps


# Objects that are maps by nature: their keys are data (paths, status codes,
# expressions, scheme names), so a dict of dicts is the object itself
_MAP_OBJECTS = frozenset({"Paths Object", "Responses Object", "Callback Object", "Security Requirement Object"})


def _load(example: oai_tables.Example) -> typing.Any:
    if example.language == "yaml":
        return yaml.safe_load(example.text)
    try:
        return json.loads(example.text)
    except json.JSONDecodeError:
        # The spec often shows a bare member, `"key": {...}`, which is only valid inside braces
        if example.text.lstrip().startswith('"'):
            return json.loads("{" + example.text + "}")
        raise


def _unwrap(data: dict[str, typing.Any]) -> list[tuple[str, typing.Any]]:
    """Expand container keys (``servers``, ``components`` ...) into the objects they hold."""
    targets: list[tuple[str, typing.Any]] = []
    for key, value in data.items():
        target, container = models.CONTAINER_KEYS[key]
        if container == "one":
            targets.append((target, value))
        elif isinstance(value, list):
            targets.extend((target, item) for item in value)
        elif isinstance(value, dict):
            targets.extend((target, item) for item in value.values())
        else:
            targets.append((target, value))
    return targets


def _targets(object_name: str | None, data: typing.Any) -> list[tuple[str, typing.Any]] | None:
    """Resolve an example's shape into the (object, value) pairs it actually shows.

    Returns None when an example outside any object section is not a document fragment.
    """
    is_fragment = isinstance(data, dict) and data and set(data) <= set(models.CONTAINER_KEYS)
    # Outside an object section, a dict of container keys is a partial document
    # (``components:`` plus ``paths:``). Inside one, only a single wrapping key
    # counts, since an object's own fields can share those names.
    if is_fragment and (object_name is None or len(data) == 1):
        return _unwrap(data)
    if object_name is None:
        return None
    model = models.MODELS.get(object_name)
    if (
        object_name not in _MAP_OBJECTS
        and model is not None
        and isinstance(data, dict)
        and data
        and all(isinstance(value, dict) for value in data.values())
        and not set(data) & models.wire_names(model)
    ):
        # A map of names to objects, such as `"X-Rate-Limit-Limit": {...}` under Header Object
        return [(object_name, value) for value in data.values()]
    return [(object_name, data)]


def example_failure(example: oai_tables.Example) -> str | None:
    """Why an example does not parse, or None if it does."""
    try:
        data = _load(example)
    except (json.JSONDecodeError, yaml.YAMLError) as error:
        return f"not loadable as {example.language}: {str(error).splitlines()[0]}"

    if isinstance(data, dict) and "openapi" in data:
        targets: list[tuple[str, typing.Any]] | None = [("OpenAPI Object", data)]
    else:
        section = example.object_name and models.EXAMPLE_OBJECT.get(example.object_name, example.object_name)
        targets = _targets(section, data)
    if targets is None:
        return f"not an OpenAPI object or document fragment (under '{example.heading}')"

    for object_name, value in targets:
        builder = cicerone.parse_spec_from_dict if object_name == "OpenAPI Object" else models.BUILDERS.get(object_name)
        if builder is None:
            return f"no way to parse a {object_name} on its own"
        if not isinstance(value, dict):
            return f"{object_name} example is a {type(value).__name__}, not an object"
        try:
            builder(value)
        except Exception as error:
            first_line = str(error).splitlines()[0] if str(error) else ""
            return f"{object_name}: {type(error).__name__}: {first_line}".rstrip(": ")
    return None


def example_failures() -> dict[str, tuple[oai_tables.Example, str]]:
    """Failing examples keyed by a stable id: object section plus content hash.

    The same block often appears in several versions; it gets one entry, keyed
    without the version, since it parses the same way in each.
    """
    failures: dict[str, tuple[oai_tables.Example, str]] = {}
    for version in oai_tables.spec_versions():
        for example in oai_tables.examples(version):
            reason = example_failure(example)
            if reason is not None:
                failures.setdefault(example_key(example), (example, reason))
    return failures


def example_key(example: oai_tables.Example) -> str:
    section = example.object_name or "(no object)"
    return f"{section}/{example.key.split(':', 1)[1]}"
