"""Exceptions raised by cicerone.

Every exception derives from ``CiceroneError`` so callers can catch cicerone
failures in one place. Reference failures share ``RefResolutionError`` so a
caller that only cares that a ``$ref`` could not be followed need not list
every way that can happen.
"""

from __future__ import annotations

import typing


class CiceroneError(Exception):
    """Base class for every error cicerone raises."""


class ParseError(CiceroneError):
    """A document could not be parsed under ``strict=True``.

    ``diagnostics`` holds every error-severity diagnostic from the full walk,
    not just the first one found.
    """

    def __init__(self, message: str, *, diagnostics: typing.Sequence[typing.Any] = ()) -> None:
        super().__init__(message)
        self.diagnostics = tuple(diagnostics)


class UnsupportedVersionError(CiceroneError):
    """The document is not OpenAPI 3.0, 3.1 or 3.2 (for example Swagger 2.0)."""


class RefResolutionError(CiceroneError):
    """A ``$ref`` could not be followed to its target."""

    def __init__(self, message: str, *, ref: str, location: typing.Any = None) -> None:
        super().__init__(message)
        self.ref = ref
        self.location = location


class CircularReferenceError(RefResolutionError):
    """Following a ``$ref`` chain led back to a reference already being followed."""


class RemoteRefDisallowedError(RefResolutionError):
    """A ``$ref`` points at a remote document but remote references are not allowed."""
