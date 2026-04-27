"""CLI helpers for baseline comparison feature."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from csvdiff.baseline import (
    BaselineError,
    BaselineComparison,
    compare_to_baseline,
    format_baseline_comparison,
    save_baseline,
)
from csvdiff.differ import DiffResult


def register_baseline_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("baseline")
    grp.add_argument(
        "--save-baseline",
        metavar="FILE",
        default=None,
        help="Save the current diff result as a baseline to FILE.",
    )
    grp.add_argument(
        "--compare-baseline",
        metavar="FILE",
        default=None,
        help="Compare the current diff against a saved baseline FILE.",
    )
    grp.add_argument(
        "--baseline-json",
        action="store_true",
        default=False,
        help="Output baseline comparison as JSON.",
    )


def baseline_comparison_as_dict(cmp: BaselineComparison) -> dict[str, Any]:
    return {
        "is_clean": cmp.is_clean,
        "new_regressions": cmp.new_regressions,
        "resolved_issues": cmp.resolved_issues,
        "unchanged_issues": cmp.unchanged_issues,
    }


def maybe_handle_baseline(
    args: argparse.Namespace,
    result: DiffResult,
) -> bool:
    """Handle baseline save/compare.  Returns True if a compare was performed."""
    import json

    if getattr(args, "save_baseline", None):
        try:
            save_baseline(result, args.save_baseline)
            print(f"Baseline saved to {args.save_baseline}", file=sys.stderr)
        except OSError as exc:
            print(f"Error saving baseline: {exc}", file=sys.stderr)
            sys.exit(1)

    if getattr(args, "compare_baseline", None):
        try:
            cmp = compare_to_baseline(result, args.compare_baseline)
        except BaselineError as exc:
            print(f"Baseline error: {exc}", file=sys.stderr)
            sys.exit(1)

        if getattr(args, "baseline_json", False):
            print(json.dumps(baseline_comparison_as_dict(cmp), indent=2))
        else:
            print(format_baseline_comparison(cmp))

        return True

    return False
