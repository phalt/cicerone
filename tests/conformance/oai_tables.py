"""Extract fixed fields and examples from the vendored OpenAPI specification markdown.

The OAI publishes each version as one markdown file. Every object is a heading
ending in "Object", followed by tables whose header is either "Field Name"
(fixed fields) or "Field Pattern" (patterned fields such as ``/{path}`` or
``^x-``). Field rows start with an HTML anchor: ``| <a name="..."></a>field |``.
Examples are fenced ```yaml / ```json blocks.
"""

from __future__ import annotations

import dataclasses
import hashlib
import pathlib
import re

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "oai"

# The latest patch of each minor carries anchored tables; earlier patches use
# an older table format, and patch releases never add fields
FIELD_SOURCES = ("3.0.4", "3.1.2", "3.2.1")

_HEADING = re.compile(r"^(#+)\s+(.+?)\s*$")
_OBJECT_HEADING = re.compile(r"^(?P<name>[A-Z][A-Za-z ]*? Object)$")
_TABLE_HEADER = re.compile(r"^\|\s*Field (?P<kind>Name|Pattern)\s*\|")
_FIELD_ROW = re.compile(r'^\|\s*<a name="[^"]*"></a>\s*(?P<field>[^|]+?)\s*\|')
_FENCE_OPEN = re.compile(r"^```(?P<lang>yaml|json)\s*$", re.IGNORECASE)


@dataclasses.dataclass(frozen=True, slots=True)
class FixedField:
    version: str
    object_name: str
    field: str


@dataclasses.dataclass(frozen=True, slots=True)
class Example:
    version: str
    language: str
    # Nearest enclosing "... Object" heading, or None when the block sits elsewhere
    object_name: str | None
    # Nearest heading of any kind, kept for allowlist reasons and debugging
    heading: str
    line: int
    text: str

    @property
    def key(self) -> str:
        """A stable identifier: version plus a content hash, independent of position in the file."""
        digest = hashlib.sha256(self.text.encode()).hexdigest()[:12]
        return f"{self.version}:{digest}"


def spec_versions() -> list[str]:
    """Every vendored specification version, oldest first."""
    names = (p.stem for p in FIXTURES.glob("3.*.md"))
    return sorted(names, key=lambda v: tuple(int(part) for part in v.split(".")))


def _read(version: str) -> list[str]:
    return (FIXTURES / f"{version}.md").read_text(encoding="utf-8").splitlines()


def _object_level(lines: list[str]) -> int:
    """Heading depth used for object sections in this file, taken from the Info Object heading.

    Example subsections such as "No XML Object" also end in "Object" but sit
    deeper, so only headings at this exact depth start an object section.
    """
    for line in lines:
        if (heading := _HEADING.match(line)) and heading.group(2) == "Info Object":
            return len(heading.group(1))
    raise ValueError("No Info Object heading found")


def _object_name(line: str, level: int) -> str | None:
    """The object a heading introduces, or None if it is not an object heading."""
    heading = _HEADING.match(line)
    if heading and len(heading.group(1)) == level and (match := _OBJECT_HEADING.match(heading.group(2))):
        return match.group("name")
    return None


def fixed_fields(version: str) -> list[FixedField]:
    """Fixed fields of every object, in document order. Patterned fields are excluded."""
    lines = _read(version)
    level = _object_level(lines)
    fields: list[FixedField] = []
    current_object: str | None = None
    table_kind: str | None = None
    for line in lines:
        if heading := _HEADING.match(line):
            if len(heading.group(1)) <= level:
                current_object = _object_name(line, level)
            table_kind = None
            continue
        if header := _TABLE_HEADER.match(line):
            table_kind = header.group("kind")
            continue
        if not line.startswith("|"):
            table_kind = None
            continue
        if table_kind == "Name" and current_object and (row := _FIELD_ROW.match(line)):
            fields.append(FixedField(version, current_object, row.group("field")))
    return fields


def examples(version: str) -> list[Example]:
    """Every fenced YAML and JSON block, with the object section it appears in."""
    lines = _read(version)
    level = _object_level(lines)
    found: list[Example] = []
    current_object: str | None = None
    heading_text = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        if heading := _HEADING.match(line):
            heading_text = heading.group(2)
            if len(heading.group(1)) <= level:
                # A heading at object depth or above starts a new section, object or not
                current_object = _object_name(line, level)
        elif fence := _FENCE_OPEN.match(line.strip()):
            start = index
            body: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                body.append(lines[index])
                index += 1
            found.append(
                Example(
                    version=version,
                    language=fence.group("lang").lower(),
                    object_name=current_object,
                    heading=heading_text,
                    line=start + 1,
                    text="\n".join(body) + "\n",
                )
            )
        index += 1
    return found
