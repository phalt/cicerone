"""Tests for the pure helpers in scripts/clientele_smoke.py.

The script itself runs clientele end to end in CI; these cover the logic that
decides what it runs and how it judges the result.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import types

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "clientele_smoke.py"


@pytest.fixture(scope="module")
def smoke() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("clientele_smoke", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["clientele_smoke"] = module
    spec.loader.exec_module(module)
    return module


PYPROJECT = """
[project]
name = "clientele"
dependencies = ["httpx2>=2.2.0", "pydantic>=2.12.5"]

[project.optional-dependencies]
core = []
cli = ["click>=8.3.1", "cicerone==0.3.0", "Cicerone>=0.1", "jinja2>=3.1.6"]
"""


def test_requirements_drop_every_cicerone_pin(smoke: types.ModuleType) -> None:
    assert smoke.requirements(PYPROJECT) == ["httpx2>=2.2.0", "pydantic>=2.12.5", "click>=8.3.1", "jinja2>=3.1.6"]


@pytest.mark.parametrize(
    ("relative", "expected"),
    [
        ("example_openapi_specs/best.json", "example_openapi_specs_best_json"),
        ("tests/fixtures/realworld/1password.yaml", "tests_fixtures_realworld_1password_yaml"),
        ("server_examples/django-ninja/openapi.json", "server_examples_django_ninja_openapi_json"),
        ("3d/spec.yaml", "fixture_3d_spec_yaml"),
    ],
)
def test_package_names_are_importable_identifiers(smoke: types.ModuleType, relative: str, expected: str) -> None:
    name = smoke.package_name(pathlib.PurePosixPath(relative))
    assert name == expected
    assert name.isidentifier()


def test_discovers_specs_in_the_three_fixture_roots_only(smoke: types.ModuleType, tmp_path: pathlib.Path) -> None:
    for relative in [
        "example_openapi_specs/a.json",
        "tests/fixtures/b.yaml",
        "tests/fixtures/deep/c.yml",
        "server_examples/d/openapi.json",
        "docs/not-a-fixture.json",
        "tests/fixtures/notes.txt",
    ]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")

    found = [p.relative_to(tmp_path).as_posix() for p in smoke.discover(tmp_path)]

    assert found == [
        "example_openapi_specs/a.json",
        "server_examples/d/openapi.json",
        "tests/fixtures/b.yaml",
        "tests/fixtures/deep/c.yml",
    ]


def test_compare_reports_changed_missing_and_identical_files(smoke: types.ModuleType, tmp_path: pathlib.Path) -> None:
    generated, baseline = tmp_path / "generated", tmp_path / "baseline"
    for directory in (generated, baseline):
        directory.mkdir()
    (generated / "client.py").write_text("same\n")
    (baseline / "client.py").write_text("same\n")
    (generated / "schemas.py").write_text("new\n")
    (baseline / "schemas.py").write_text("old\n")

    assert smoke.compare(generated, baseline) == ["schemas.py differs"]

    (baseline / "schemas.py").unlink()
    assert smoke.compare(generated, baseline) == ["schemas.py missing from baseline"]


def test_known_failures_are_tolerated_and_fixed_ones_are_flagged(smoke: types.ModuleType) -> None:
    results = [
        smoke.Result("a.json", "failed", "import failed: NameError"),
        smoke.Result("b.json", "ok"),
        smoke.Result("c.json", "failed", "generate exited 1"),
        smoke.Result("d.json", "skipped", "empty file"),
    ]
    known = {"a.json": "clientele bug", "b.json": "clientele bug, since fixed"}

    judged = {r.fixture: (r.status, r.detail) for r in smoke.apply_known_failures(results, known)}

    assert judged == {
        "a.json": ("known", "clientele bug"),
        "b.json": ("fixed", "now passes; remove from known failures"),
        "c.json": ("failed", "generate exited 1"),
        "d.json": ("skipped", "empty file"),
    }


def test_exit_code_fails_on_new_failures_and_stale_known_failures(smoke: types.ModuleType) -> None:
    assert smoke.exit_code([smoke.Result("a", "ok"), smoke.Result("b", "known"), smoke.Result("c", "skipped")]) == 0
    assert smoke.exit_code([smoke.Result("a", "differs")]) == 2
    assert smoke.exit_code([smoke.Result("a", "differs"), smoke.Result("b", "failed")]) == 1
    assert smoke.exit_code([smoke.Result("a", "fixed")]) == 1


def test_known_failures_file_maps_fixtures_to_reasons(smoke: types.ModuleType) -> None:
    known = smoke.load_known_failures(smoke.KNOWN_FAILURES)

    assert known
    assert all(reason.strip() for reason in known.values())


def test_baseline_ignores_files_that_embed_paths_or_versions(smoke: types.ModuleType) -> None:
    # MANIFEST.md records the output path and clientele version; config.py is user-owned
    assert smoke.COMPARED_FILES == ("client.py", "schemas.py")
