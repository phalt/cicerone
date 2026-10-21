"""Every YAML and JSON example in the OpenAPI 3.0.0 to 3.2.1 specifications parses.

Full documents go through the parser; fragments are built as the object their
section describes, after unwrapping the parent key the spec often shows them
under. Known failures live in tests/fixtures/oai/allowlist.toml under
[examples]. The list only shrinks: a new failure fails, and so does an
allowlisted example that now parses but was not removed.
"""

import pytest

from . import checks, oai_tables

# Pinned so a change in the vendored markdown, or an extractor regression,
# cannot silently shrink what is being checked
EXPECTED_EXAMPLE_COUNT = 1381


def test_extracts_every_example() -> None:
    assert sum(len(oai_tables.examples(version)) for version in oai_tables.spec_versions()) == EXPECTED_EXAMPLE_COUNT


def test_vendors_every_released_3x_version() -> None:
    assert oai_tables.spec_versions() == [
        "3.0.0",
        "3.0.1",
        "3.0.2",
        "3.0.3",
        "3.0.4",
        "3.1.0",
        "3.1.1",
        "3.1.2",
        "3.2.0",
        "3.2.1",
    ]


@pytest.fixture(scope="module")
def failures() -> dict[str, tuple[oai_tables.Example, str]]:
    return checks.example_failures()


def test_no_failing_example_outside_the_allowlist(failures: dict[str, tuple[oai_tables.Example, str]]) -> None:
    allowed = checks.allowlist("examples")
    unexpected = [
        f"{key} ({example.version} line {example.line}): {reason}"
        for key, (example, reason) in sorted(failures.items())
        if key not in allowed
    ]

    assert not unexpected, "Spec examples that fail to parse (fix, or allowlist with a reason):\n" + "\n".join(
        unexpected
    )


def test_allowlist_has_no_fixed_examples(failures: dict[str, tuple[oai_tables.Example, str]]) -> None:
    fixed = sorted(set(checks.allowlist("examples")) - set(failures))

    assert not fixed, "Now parses; remove from [examples] in allowlist.toml:\n" + "\n".join(fixed)


def test_every_allowlist_entry_has_a_reason() -> None:
    for section in ("fields", "examples"):
        for key, reason in checks.allowlist(section).items():
            assert reason.strip(), f"[{section}] {key} needs a reason"
            assert reason.startswith(checks.PERMANENT_PREFIXES) or "(Task " in reason, (
                f"[{section}] {key}: reason must name the closing task or start with 'by design:' / 'erratum:'"
            )
