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


def test_schema_file(schema_path: pathlib.Path) -> Tuple[str, str, Exception | None]:
    """Test parsing a single schema file.

    Returns:
        Tuple of (status: str, error_message: str, exception: Exception | None)
        where status is one of: "success", "skipped", "failed"
    """
    try:
        spec = cicerone_parse.parse_spec_from_file(schema_path)
        # Basic validation - ensure we got a spec with some content
        if spec is None:
            return "failed", "Parsed spec is None", None
        
        # Check if this is a Swagger 2.x file (even if cicerone auto-converts it)
        # Cicerone preserves the original format in spec.raw
        if "swagger" in spec.raw:
            swagger_version = spec.raw["swagger"]
            # Check if it's Swagger 2.x (2.0, 2.1, etc.)
            try:
                # Handle both string and numeric versions
                version_str = str(swagger_version)
                # Ensure version_str is not empty and has at least one part
                if version_str and version_str.split(".")[0] == "2":
                    return "skipped", f"Swagger {version_str} (not supported, cicerone requires OpenAPI 3.x)", None
            except (IndexError, ValueError):
                pass  # If we can't parse version, continue with normal processing
        
        return "success", "", None
    except Exception as e:
        return "failed", f"{type(e).__name__}: {str(e)}", e


def test_all_schemas(
    schema_files: List[pathlib.Path], base_dir: pathlib.Path, verbose: bool = False, fail_fast: bool = False
) -> Tuple[int, int, int, List[Tuple[pathlib.Path, str, Exception | None]], List[Tuple[pathlib.Path, str]]]:
    """Test parsing all schema files.

    Returns:
        Tuple of (success_count, skipped_count, failure_count, failures_list, skipped_list)
    """
    print(f"\nTesting {len(schema_files)} schemas...")
    successes = 0
    skipped = []
    failures = []

    for i, schema_path in enumerate(schema_files, 1):
        if verbose or i % 100 == 0:
            print(
                f"Progress: {i}/{len(schema_files)} ({successes} successful, "
                f"{len(skipped)} skipped, {len(failures)} failed)"
            )

        status, error, exception = test_schema_file(schema_path)
        if status == "success":
            successes += 1
            if verbose:
                print(f"  ✓ {schema_path.relative_to(base_dir)}")
        elif status == "skipped":
            skipped.append((schema_path, error))
            if verbose:
                print(f"  ⊘ {schema_path.relative_to(base_dir)}: {error}")
        else:  # failed
            failures.append((schema_path, error, exception))
            if verbose:
                print(f"  ✗ {schema_path.relative_to(base_dir)}: {error}")

            if fail_fast:
                print(f"\n{'=' * 80}")
                print("FAIL FAST MODE - Stopping on first error")
                print(f"{'=' * 80}")
                print(f"Failed schema: {schema_path.relative_to(base_dir)}")
                print(f"Error: {error}")
                if exception:
                    print("\nFull error details:")
                    import traceback

                    traceback.print_exception(type(exception), exception, exception.__traceback__)
                print(f"\nSchema location: {schema_path}")
                break

    return successes, len(skipped), len(failures), failures, skipped


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
    parser.add_argument(
        "-x", "--fail-fast", action="store_true", help="Stop on first failure and print detailed error info"
    )
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
        successes, skipped_count, failures_count, failures, skipped = test_all_schemas(
            schema_files, repo_dir, verbose=args.verbose, fail_fast=args.fail_fast
        )

        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total schemas found: {len(schema_files)}")
        print(f"Successful: {successes}")
        print(f"Skipped (version incompatible): {skipped_count}")
        print(f"Failed: {failures_count}")

        # Calculate success rate excluding skipped schemas
        testable_count = len(schema_files) - skipped_count
        if testable_count > 0:
            success_rate = successes / testable_count * 100
            print(
                f"Success rate: {success_rate:.2f}% ({successes}/{testable_count} testable schemas)"
            )
        else:
            # Output 0.00% for consistency with badge extraction
            print("Success rate: 0.00% (no testable schemas)")

        if skipped:
            print(f"\n{len(skipped)} schemas skipped due to version incompatibility:")
            for schema_path, reason in skipped[:5]:  # Show first 5 skipped
                rel_path = schema_path.relative_to(repo_dir)
                print(f"  - {rel_path}")
                if args.verbose:
                    print(f"    Reason: {reason}")

            if len(skipped) > 5:
                print(f"  ... and {len(skipped) - 5} more")

        if failures:
            print(f"\n{len(failures)} schemas failed to parse:")
            for schema_path, error, _ in failures[:10]:  # Show first 10 failures
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
