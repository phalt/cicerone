"""Generate and import a clientele client for every clientele fixture, using this cicerone.

clientele is cicerone's main consumer. This runs clientele's own CLI over the
OpenAPI fixtures in a clientele checkout, with whichever cicerone is installed
in the current environment, then imports each generated package. A crash in
generation or an import error is a failure.

Setup, from the cicerone repository (clientele pins an older cicerone, so it
is installed without dependencies and its other requirements are added):

    uv sync
    uv pip install --no-deps ../clientele
    uv pip install $(uv run --no-sync python scripts/clientele_smoke.py requirements ../clientele)

Usage:

    uv run --no-sync python scripts/clientele_smoke.py run ../clientele
    uv run --no-sync python scripts/clientele_smoke.py run ../clientele --write-baseline smoke-baseline
    uv run --no-sync python scripts/clientele_smoke.py run ../clientele --baseline smoke-baseline

Fixtures that already fail with clientele's own pinned cicerone are listed in
scripts/clientele_known_failures.toml with a reason; they report as "known".
A known failure that starts working reports as "fixed" and fails the run, so
the list only shrinks.

Exit codes: 0 all good, 1 a fixture failed to generate or import (or a known
failure was fixed and needs removing), 2 every fixture worked but output
differs from the baseline.
"""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

FIXTURE_ROOTS = ("example_openapi_specs", "server_examples", "tests/fixtures")
SPEC_SUFFIXES = frozenset({".json", ".yaml", ".yml"})
# Generated files compared against a baseline. MANIFEST.md records the output
# path and clientele version, and config.py belongs to the user once generated.
COMPARED_FILES = ("client.py", "schemas.py")
TIMEOUT_SECONDS = 180
KNOWN_FAILURES = pathlib.Path(__file__).resolve().with_name("clientele_known_failures.toml")

_CICERONE_REQUIREMENT = re.compile(r"^\s*cicerone\b", re.IGNORECASE)
_NOT_IDENTIFIER = re.compile(r"\W")


def requirements(pyproject_text: str) -> list[str]:
    """clientele's runtime and CLI requirements, without its cicerone pin."""
    project = tomllib.loads(pyproject_text)["project"]
    wanted = [*project.get("dependencies", []), *project.get("optional-dependencies", {}).get("cli", [])]
    return [requirement for requirement in wanted if not _CICERONE_REQUIREMENT.match(requirement)]


def package_name(relative: pathlib.PurePath) -> str:
    """A unique, importable package name for a fixture's generated client."""
    name = _NOT_IDENTIFIER.sub("_", relative.as_posix())
    return f"fixture_{name}" if name[0].isdigit() else name


def discover(clientele_dir: pathlib.Path) -> list[pathlib.Path]:
    """Every OpenAPI fixture under clientele's fixture roots, in a stable order."""
    found = [
        path
        for root in FIXTURE_ROOTS
        if (clientele_dir / root).is_dir()
        for path in (clientele_dir / root).rglob("*")
        if path.is_file() and path.suffix in SPEC_SUFFIXES
    ]
    return sorted(found, key=lambda path: path.relative_to(clientele_dir).as_posix())


def compare(generated: pathlib.Path, baseline: pathlib.Path) -> list[str]:
    """Differences between a generated client and its baseline, one line each."""
    differences = []
    for name in COMPARED_FILES:
        if not (baseline / name).exists():
            differences.append(f"{name} missing from baseline")
        elif (generated / name).read_text() != (baseline / name).read_text():
            differences.append(f"{name} differs")
    return differences


@dataclasses.dataclass(slots=True)
class Result:
    fixture: str
    status: str  # ok, skipped, differs, failed, known (expected failure) or fixed (known failure now passing)
    detail: str = ""


def load_known_failures(path: pathlib.Path) -> dict[str, str]:
    """Fixtures expected to fail, as relative path to reason."""
    with path.open("rb") as handle:
        return tomllib.load(handle).get("known_failures", {})


def apply_known_failures(results: list[Result], known: dict[str, str]) -> list[Result]:
    """Mark expected failures as known, and known failures that now work as fixed."""
    judged = []
    for result in results:
        if result.fixture in known and result.status == "failed":
            judged.append(Result(result.fixture, "known", known[result.fixture]))
        elif result.fixture in known and result.status != "skipped":
            judged.append(Result(result.fixture, "fixed", "now passes; remove from known failures"))
        else:
            judged.append(result)
    return judged


def exit_code(results: list[Result]) -> int:
    statuses = {result.status for result in results}
    if statuses & {"failed", "fixed"}:
        return 1
    return 2 if "differs" in statuses else 0


def _run(arguments: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments], cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False
    )


def _last_line(process: subprocess.CompletedProcess[str]) -> str:
    output = (process.stderr or process.stdout).strip().splitlines()
    return output[-1] if output else f"exit code {process.returncode}"


def _generate(spec: pathlib.Path, output: pathlib.Path, work: pathlib.Path) -> str | None:
    """Run clientele's CLI; return why it failed, or None."""
    cli = "import sys; from clientele.cli import cli_group; sys.exit(cli_group(prog_name='clientele'))"
    process = _run(["-c", cli, "start-api", "-f", str(spec), "-o", str(output), "--regen"], cwd=work)
    if process.returncode != 0:
        return f"generate exited {process.returncode}: {_last_line(process)}"
    # clientele logs some failures (an unsupported version, say) and still exits 0
    if missing := [name for name in COMPARED_FILES if not (output / name).is_file()]:
        return f"generate wrote no {', '.join(missing)}: {_last_line(process)}"
    return None


def _import(package: str, work: pathlib.Path) -> str | None:
    """Import the generated client and schemas; return why it failed, or None."""
    code = (
        f"import importlib; importlib.import_module('{package}.schemas'); importlib.import_module('{package}.client')"
    )
    process = _run(["-c", code], cwd=work)
    return None if process.returncode == 0 else f"import failed: {_last_line(process)}"


def smoke(
    clientele_dir: pathlib.Path,
    work: pathlib.Path,
    *,
    baseline: pathlib.Path | None = None,
    write_baseline: pathlib.Path | None = None,
) -> list[Result]:
    results = []
    for spec in discover(clientele_dir):
        relative = spec.relative_to(clientele_dir)
        package = package_name(relative)
        if spec.stat().st_size == 0:
            results.append(Result(relative.as_posix(), "skipped", "empty file"))
            continue
        output = work / package
        if failure := _generate(spec, output, work) or _import(package, work):
            results.append(Result(relative.as_posix(), "failed", failure))
            continue
        if write_baseline is not None:
            (write_baseline / package).mkdir(parents=True, exist_ok=True)
            for name in COMPARED_FILES:
                shutil.copyfile(output / name, write_baseline / package / name)
        if baseline is not None and (differences := compare(output, baseline / package)):
            results.append(Result(relative.as_posix(), "differs", "; ".join(differences)))
            continue
        results.append(Result(relative.as_posix(), "ok"))
    return results


def _report(results: list[Result]) -> int:
    for result in results:
        print(f"{result.status:<8} {result.fixture}" + (f"  ({result.detail})" if result.detail else ""))
    statuses = ("ok", "known", "skipped", "differs", "fixed", "failed")
    counts = {status: sum(r.status == status for r in results) for status in statuses}
    print("\n" + ", ".join(f"{count} {status}" for status, count in counts.items() if count))
    return exit_code(results)


def main(argv: list[str] | None = None) -> int:
    # __doc__ is None under python -OO
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)

    requirements_command = commands.add_parser("requirements", help="print clientele's requirements minus cicerone")
    requirements_command.add_argument("clientele_dir", type=pathlib.Path)

    run_command = commands.add_parser("run", help="generate and import every fixture")
    run_command.add_argument("clientele_dir", type=pathlib.Path)
    baselines = run_command.add_mutually_exclusive_group()
    baselines.add_argument("--baseline", type=pathlib.Path, help="compare generated files against this directory")
    baselines.add_argument("--write-baseline", type=pathlib.Path, help="save generated files to this directory")
    run_command.add_argument("--keep", type=pathlib.Path, help="generate into this directory instead of a temp one")
    run_command.add_argument(
        "--known-failures", type=pathlib.Path, default=KNOWN_FAILURES, help="TOML of fixtures expected to fail"
    )

    args = parser.parse_args(argv)
    clientele_dir = args.clientele_dir.resolve()

    if args.command == "requirements":
        print("\n".join(requirements((clientele_dir / "pyproject.toml").read_text())))
        return 0

    with tempfile.TemporaryDirectory(prefix="clientele-smoke-") as temporary:
        work = args.keep.resolve() if args.keep else pathlib.Path(temporary)
        work.mkdir(parents=True, exist_ok=True)
        results = smoke(
            clientele_dir,
            work,
            baseline=args.baseline.resolve() if args.baseline else None,
            write_baseline=args.write_baseline.resolve() if args.write_baseline else None,
        )
        return _report(apply_known_failures(results, load_known_failures(args.known_failures)))


if __name__ == "__main__":
    sys.exit(main())
