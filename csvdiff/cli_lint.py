"""CLI helpers for the lint feature."""

import argparse
from typing import List, Dict, Any

from csvdiff.lint import lint_rows, format_lint, LintResult


def register_lint_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--lint", action="store_true", help="Run lint checks on input files")
    parser.add_argument("--lint-key", metavar="COLUMN",
                        help="Column to check for duplicate keys during lint")
    parser.add_argument("--lint-no-types", action="store_true",
                        help="Disable type consistency checks during lint")


def lint_options_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "enabled": getattr(args, "lint", False),
        "key_column": getattr(args, "lint_key", None),
        "check_types": not getattr(args, "lint_no_types", False),
    }


def maybe_run_lint(
    rows: List[Dict[str, Any]],
    columns: List[str],
    opts: Dict[str, Any],
    label: str = "file",
) -> LintResult:
    if not opts.get("enabled"):
        return LintResult()
    result = lint_rows(
        rows,
        columns,
        key_column=opts.get("key_column"),
        check_types=opts.get("check_types", True),
    )
    print(f"Lint [{label}]: {format_lint(result)}")
    return result
