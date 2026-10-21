"""Packaging and public API guarantees for the cicerone distribution."""

import importlib
import importlib.metadata
from importlib import resources

import pytest

import cicerone
import cicerone.spec
from cicerone import errors


def test_ships_py_typed_marker() -> None:
    """PEP 561: type checkers only trust cicerone's annotations if py.typed ships in the package."""
    assert resources.files("cicerone").joinpath("py.typed").is_file()


def test_version_comes_from_installed_metadata() -> None:
    assert cicerone.__version__ == importlib.metadata.version("cicerone")


def test_settings_module_is_gone() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("cicerone.settings")


@pytest.mark.parametrize(
    "name",
    [
        "parse_spec_from_dict",
        "parse_spec_from_file",
        "parse_spec_from_json",
        "parse_spec_from_url",
        "parse_spec_from_yaml",
        "Reference",
        "CiceroneError",
        "ParseError",
        "UnsupportedVersionError",
        "RefResolutionError",
        "CircularReferenceError",
        "RemoteRefDisallowedError",
    ],
)
def test_top_level_exports(name: str) -> None:
    assert name in cicerone.__all__
    assert getattr(cicerone, name) is not None


def test_every_spec_model_is_exported_at_top_level() -> None:
    for name in cicerone.spec.__all__:
        assert name in cicerone.__all__, name
        assert getattr(cicerone, name) is getattr(cicerone.spec, name)


def test_all_is_unique_and_public() -> None:
    assert len(cicerone.__all__) == len(set(cicerone.__all__))
    assert all(not name.startswith("_") for name in cicerone.__all__)


def test_star_import_exposes_exactly_all() -> None:
    namespace: dict[str, object] = {}
    exec("from cicerone import *", namespace)
    exported = {name for name in namespace if name != "__builtins__"}
    assert exported == set(cicerone.__all__)


class TestErrors:
    @pytest.mark.parametrize(
        "error",
        [
            errors.ParseError,
            errors.UnsupportedVersionError,
            errors.RefResolutionError,
            errors.CircularReferenceError,
            errors.RemoteRefDisallowedError,
        ],
    )
    def test_everything_is_a_cicerone_error(self, error: type[Exception]) -> None:
        assert issubclass(error, errors.CiceroneError)

    @pytest.mark.parametrize("error", [errors.CircularReferenceError, errors.RemoteRefDisallowedError])
    def test_ref_failures_are_catchable_as_ref_resolution_errors(self, error: type[Exception]) -> None:
        assert issubclass(error, errors.RefResolutionError)

    def test_does_not_shadow_builtin_reference_error(self) -> None:
        assert not hasattr(errors, "ReferenceError")

    def test_parse_error_carries_diagnostics(self) -> None:
        diagnostics = ("first", "second")
        error = errors.ParseError("2 errors", diagnostics=diagnostics)
        assert error.diagnostics == diagnostics
        assert str(error) == "2 errors"

    def test_parse_error_defaults_to_no_diagnostics(self) -> None:
        assert errors.ParseError("boom").diagnostics == ()

    def test_ref_resolution_error_carries_ref_and_location(self) -> None:
        error = errors.RefResolutionError("not found", ref="#/components/schemas/Pet", location="#/paths")
        assert error.ref == "#/components/schemas/Pet"
        assert error.location == "#/paths"
        assert str(error) == "not found"

    def test_subclasses_keep_ref_and_location(self) -> None:
        error = errors.CircularReferenceError("cycle", ref="#/a")
        assert error.ref == "#/a"
        assert error.location is None
