"""CLI helpers for the transform feature."""
from __future__ import annotations
import argparse
from typing import List

from csvdiff.transform import TransformError, TransformOptions, TransformRule


def register_transform_args(parser: argparse.ArgumentParser) -> None:
    """Add --transform and --transform-regex flags to *parser*."""
    parser.add_argument(
        "--transform",
        metavar="COL:FIND:REPLACE",
        action="append",
        default=[],
        help="Plain find/replace on a column value (repeatable).",
    )
    parser.add_argument(
        "--transform-regex",
        metavar="COL:PATTERN:REPLACE",
        action="append",
        default=[],
        help="Regex substitution on a column value (repeatable).",
    )


def _parse_spec(spec: str, use_regex: bool) -> TransformRule:
    parts = spec.split(":", 2)
    if len(parts) != 3:
        raise TransformError(
            f"Transform spec must be COL:FIND:REPLACE, got {spec!r}"
        )
    col, pattern, replacement = parts
    if not col or not pattern:
        raise TransformError(f"Column and pattern must not be empty in {spec!r}")
    return TransformRule(
        column=col, pattern=pattern, replacement=replacement, use_regex=use_regex
    )


def transform_options_from_args(args: argparse.Namespace) -> TransformOptions:
    rules: List[TransformRule] = []
    for spec in getattr(args, "transform", []) or []:
        rules.append(_parse_spec(spec, use_regex=False))
    for spec in getattr(args, "transform_regex", []) or []:
        rules.append(_parse_spec(spec, use_regex=True))
    return TransformOptions(rules=rules)


def maybe_apply_transform(rows, options: TransformOptions):
    from csvdiff.transform import transform_rows
    if not options.rules:
        return rows
    return transform_rows(rows, options)
