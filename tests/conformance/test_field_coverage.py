"""Every fixed field in the OpenAPI 3.0, 3.1 and 3.2 specifications maps to a typed model field.

Known gaps live in tests/fixtures/oai/allowlist.toml under [fields], each with
the task that closes it. The list only shrinks: a new gap fails, and so does
an allowlisted gap that has been closed but not removed.
"""

import pytest

from . import checks, oai_tables

# Pinned so a change in the vendored markdown, or a parser regression, cannot
# silently shrink what is being checked
EXPECTED_FIELD_COUNTS = {"3.0.4": 145, "3.1.2": 148, "3.2.1": 171}


@pytest.mark.parametrize("version", oai_tables.FIELD_SOURCES)
def test_extracts_every_fixed_field(version: str) -> None:
    assert len(oai_tables.fixed_fields(version)) == EXPECTED_FIELD_COUNTS[version]


def test_patterned_fields_are_not_counted_as_fixed() -> None:
    fields = {(f.object_name, f.field) for f in oai_tables.fixed_fields("3.2.1")}

    assert ("Paths Object", "/{path}") not in fields
    assert ("Info Object", "title") in fields


def test_no_untyped_field_outside_the_allowlist() -> None:
    unexpected = sorted(set(checks.field_gaps()) - set(checks.allowlist("fields")))

    assert not unexpected, (
        "Fixed fields with no typed model field (type them, or allowlist with a reason):\n" + "\n".join(unexpected)
    )


def test_allowlist_has_no_closed_field_gaps() -> None:
    closed = sorted(set(checks.allowlist("fields")) - set(checks.field_gaps()))

    assert not closed, "Now typed; remove from [fields] in allowlist.toml:\n" + "\n".join(closed)
