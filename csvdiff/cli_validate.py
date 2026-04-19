"""CLI integration for validation rules."""
from __future__ import annotations
import argparse
from typing import List
from csvdiff.validate import ValidationRule, ValidateError, validate_rows, format_validation


def register_validate_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--validate-not-empty",
        metavar="COL",
        nargs="+",
        default=[],
        help="Columns that must not be empty.",
    )
    parser.add_argument(
        "--validate-numeric",
        metavar="COL",
        nargs="+",
        default=[],
        help="Columns that must contain numeric values.",
    )
    parser.add_argument(
        "--validate-pattern",
        metavar="COL:PATTERN",
        nargs="+",
        default=[],
        help="Columns that must match a regex pattern (format: col:pattern).",
    )


def validation_rules_from_args(args: argparse.Namespace) -> List[ValidationRule]:
    rules: dict[str, ValidationRule] = {}

    for col in getattr(args, "validate_not_empty", []):
        rules.setdefault(col, ValidationRule(column=col)).not_empty = True

    for col in getattr(args, "validate_numeric", []):
        rules.setdefault(col, ValidationRule(column=col)).numeric = True

    for pair in getattr(args, "validate_pattern", []):
        if ":" not in pair:
            raise ValidateError(f"Invalid --validate-pattern value '{pair}': expected 'col:pattern'")
        col, pattern = pair.split(":", 1)
        rules.setdefault(col, ValidationRule(column=col)).pattern = pattern

    return list(rules.values())


def maybe_run_validation(args: argparse.Namespace, rows: list, label: str = "") -> None:
    rules = validation_rules_from_args(args)
    if not rules:
        return
    result = validate_rows(rows, rules)
    prefix = f"[{label}] " if label else ""
    print(prefix + format_validation(result))
