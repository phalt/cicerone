#!/usr/bin/env python3
"""Test script to validate cicerone against all schemas in the APIs-guru openapi-directory.

This script:
1. Clones the openapi-directory repository
2. Finds all OpenAPI schema files (.yaml, .json)
3. Attempts to parse each schema with cicerone
4. Reports results (success, failures, statistics)
"""

import argparse
import pathlib
import shutil
import subprocess
import sys
from typing import List, Tuple

from cicerone import parse as cicerone_parse


def clone_openapi_directory(target_dir: pathlib.Path) -> None:
    """Clone the openapi-directory repository."""
    print("Cloning openapi-directory repository...")
    subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/APIs-guru/openapi-directory.git", str(target_dir)],
        check=True,
        capture_output=True,
    )
    print(f"Repository cloned to {target_dir}")


def find_schema_files(base_dir: pathlib.Path) -> List[pathlib.Path]:
    """Find all OpenAPI schema files in the directory."""
    print("Finding schema files...")
    schema_files = []
    apis_dir = base_dir / "APIs"

    if not apis_dir.exists():
        raise RuntimeError(f"APIs directory not found at {apis_dir}")

    # Find all .yaml and .json files
    for pattern in ["**/*.yaml", "**/*.json"]:
        schema_files.extend(apis_dir.glob(pattern))

    print(f"Found {len(schema_files)} schema files")
    return sorted(schema_files)


def test_schema_file(schema_path: pathlib.Path) -> Tuple[bool, str]:
    """Test parsing a single schema file.

    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        spec = cicerone_parse.parse_spec_from_file(schema_path)
        # Basic validation - ensure we got a spec with some content
        if spec is None:
            return False, "Parsed spec is None"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)}"


def test_all_schemas(
    schema_files: List[pathlib.Path], base_dir: pathlib.Path, verbose: bool = False
) -> Tuple[int, int, List[Tuple[pathlib.Path, str]]]:
    """Test parsing all schema files.

    Returns:
        Tuple of (success_count, failure_count, failures_list)
    """
    print(f"\nTesting {len(schema_files)} schemas...")
    successes = 0
    failures = []

    for i, schema_path in enumerate(schema_files, 1):
        if verbose or i % 100 == 0:
            print(f"Progress: {i}/{len(schema_files)} ({successes} successful, {len(failures)} failed)")

        success, error = test_schema_file(schema_path)
        if success:
            successes += 1
            if verbose:
                print(f"  ✓ {schema_path.relative_to(base_dir)}")
        else:
            failures.append((schema_path, error))
            if verbose:
                print(f"  ✗ {schema_path.relative_to(base_dir)}: {error}")

    return successes, len(failures), failures


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test cicerone against openapi-directory schemas")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--keep-repo", action="store_true", help="Don't delete the cloned repository after testing")
    parser.add_argument(
        "--repo-dir",
        type=pathlib.Path,
        default=pathlib.Path("/tmp/openapi-directory-test"),
        help="Directory to clone the repository into",
    )
    parser.add_argument("--limit", type=int, help="Limit number of schemas to test (for quick testing)")
    args = parser.parse_args()

    repo_dir = args.repo_dir

    try:
        # Clone repository if it doesn't exist
        if not repo_dir.exists():
            clone_openapi_directory(repo_dir)
        else:
            print(f"Using existing repository at {repo_dir}")

        # Find all schema files
        schema_files = find_schema_files(repo_dir)

        # Limit schemas if requested
        if args.limit:
            print(f"Limiting to first {args.limit} schemas")
            schema_files = schema_files[: args.limit]

        # Test all schemas
        successes, failures_count, failures = test_all_schemas(schema_files, repo_dir, verbose=args.verbose)

        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total schemas tested: {len(schema_files)}")
        print(f"Successful: {successes}")
        print(f"Failed: {failures_count}")
        print(f"Success rate: {successes / len(schema_files) * 100:.2f}%")

        if failures:
            print(f"\n{len(failures)} schemas failed to parse:")
            for schema_path, error in failures[:10]:  # Show first 10 failures
                rel_path = schema_path.relative_to(repo_dir)
                print(f"  - {rel_path}")
                if args.verbose:
                    print(f"    Error: {error}")

            if len(failures) > 10:
                print(f"  ... and {len(failures) - 10} more")

        return 0 if failures_count == 0 else 1

    finally:
        # Clean up unless --keep-repo is specified
        if not args.keep_repo and repo_dir.exists():
            print(f"\nCleaning up: removing {repo_dir}")
            shutil.rmtree(repo_dir)


if __name__ == "__main__":
    sys.exit(main())
