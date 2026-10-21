"""Packaging guarantees for the cicerone distribution."""

from importlib import resources


def test_ships_py_typed_marker() -> None:
    """PEP 561: type checkers only trust cicerone's annotations if py.typed ships in the package."""
    assert resources.files("cicerone").joinpath("py.typed").is_file()
