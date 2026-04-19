"""CLI helpers for column rename feature."""
from argparse import ArgumentParser, Namespace
from typing import List, Tuple, Dict

from csvdiff.rename import RenameOptions, build_rename_options, apply_renames, RenameError


def register_rename_args(parser: ArgumentParser) -> None:
    """Add --rename argument to an argument parser."""
    parser.add_argument(
        "--rename",
        metavar="OLD:NEW",
        action="append",
        default=[],
        help="Rename a column before diffing, e.g. --rename old_name:new_name",
    )


def rename_options_from_args(args: Namespace) -> RenameOptions:
    """Build RenameOptions from parsed CLI args."""
    pairs: List[str] = getattr(args, "rename", []) or []
    try:
        return build_rename_options(pairs)
    except RenameError as exc:
        raise SystemExit(f"rename error: {exc}") from exc


def maybe_apply_renames(
    rows_a: List[Dict[str, str]],
    rows_b: List[Dict[str, str]],
    options: RenameOptions,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Apply renames if any mapping is defined, otherwise return inputs unchanged."""
    if not options.mapping:
        return rows_a, rows_b
    return apply_renames(rows_a, rows_b, options)
