"""Vendor the OpenAPI specification markdown that the conformance tests read.

Copies every released 3.x version (``versions/3.*.md``, excluding the
``-editors`` drafts) from OAI/OpenAPI-Specification at a pinned commit into
``tests/fixtures/oai/``, and records the commit in ``SOURCE``. Tests never
touch the network; rerun this to move the pin.

Usage:
    uv run python scripts/refresh_oai.py [COMMIT]

Without a COMMIT the pin in tests/fixtures/oai/SOURCE is reused, which makes a
clean rerun a no-op.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPOSITORY = "https://github.com/OAI/OpenAPI-Specification.git"
DESTINATION = pathlib.Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "oai"
SOURCE_FILE = DESTINATION / "SOURCE"
RELEASED_VERSION = re.compile(r"^3\.\d+\.\d+\.md$")


def pinned_commit() -> str:
    for line in SOURCE_FILE.read_text().splitlines():
        if line.startswith("commit: "):
            return line.removeprefix("commit: ").strip()
    raise SystemExit(f"No commit recorded in {SOURCE_FILE}")


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def refresh(commit: str) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        checkout = pathlib.Path(tmp)
        git("init", "-q", cwd=checkout)
        git("remote", "add", "origin", REPOSITORY, cwd=checkout)
        git("fetch", "-q", "--depth", "1", "origin", commit, cwd=checkout)
        git("checkout", "-q", "FETCH_HEAD", cwd=checkout)
        resolved = git("rev-parse", "HEAD", cwd=checkout)
        committed_at = git("log", "-1", "--format=%cI", cwd=checkout)

        for old in DESTINATION.glob("3.*.md"):
            old.unlink()
        copied = sorted(p.name for p in (checkout / "versions").iterdir() if RELEASED_VERSION.match(p.name))
        for name in copied:
            shutil.copyfile(checkout / "versions" / name, DESTINATION / name)

    SOURCE_FILE.write_text(
        f"repository: {REPOSITORY}\n"
        f"commit: {resolved}\n"
        f"committed: {committed_at}\n"
        "files: versions/3.*.md (released versions only, -editors drafts excluded)\n"
        "license: Apache-2.0 (OpenAPI Specification text)\n"
        "refresh: uv run python scripts/refresh_oai.py [COMMIT]\n"
    )
    return copied


def main() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    commit = sys.argv[1] if len(sys.argv) > 1 else pinned_commit()
    copied = refresh(commit)
    print(f"Vendored {len(copied)} files at {commit}: {', '.join(copied)}")


if __name__ == "__main__":
    main()
