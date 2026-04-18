"""CLI integration for threshold options."""
import argparse
from csvdiff.threshold import ThresholdOptions, check_threshold, format_threshold_warning
from csvdiff.differ import DiffResult


def register_threshold_args(parser: argparse.ArgumentParser) -> None:
    g = parser.add_argument_group("threshold")
    g.add_argument("--max-added", type=int, default=None, metavar="N",
                   help="Fail if more than N rows were added")
    g.add_argument("--max-removed", type=int, default=None, metavar="N",
                   help="Fail if more than N rows were removed")
    g.add_argument("--max-modified", type=int, default=None, metavar="N",
                   help="Fail if more than N rows were modified")
    g.add_argument("--max-total-changes", type=int, default=None, metavar="N",
                   help="Fail if total changes exceed N")
    g.add_argument("--max-added-pct", type=float, default=None, metavar="PCT",
                   help="Fail if added rows exceed PCT%% of total")
    g.add_argument("--max-removed-pct", type=float, default=None, metavar="PCT",
                   help="Fail if removed rows exceed PCT%% of total")


def threshold_options_from_args(args: argparse.Namespace) -> ThresholdOptions:
    return ThresholdOptions(
        max_added=args.max_added,
        max_removed=args.max_removed,
        max_modified=args.max_modified,
        max_total=args.max_total_changes,
        max_added_pct=args.max_added_pct,
        max_removed_pct=args.max_removed_pct,
    )


def maybe_apply_threshold(result: DiffResult, options: ThresholdOptions,
                          total_rows: int = 0, color: bool = False) -> int:
    """Print warning and return exit code 2 if threshold exceeded, else 0."""
    if check_threshold(result, options, total_rows):
        return 0
    warning = format_threshold_warning(result, options, total_rows)
    if color:
        print(f"\033[33m{warning}\033[0m")
    else:
        print(warning)
    return 2
