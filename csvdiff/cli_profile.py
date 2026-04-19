"""CLI helpers for the --profile feature."""
from __future__ import annotations
import argparse
from typing import Dict, List, Optional

from csvdiff.profile import profile_rows, format_profile, ProfileResult


def register_profile_args(parser: argparse.ArgumentParser) -> None:
    """Add --profile flag to an argument parser."""
    parser.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="Print per-column statistics for each input file.",
    )
    parser.add_argument(
        "--profile-json",
        action="store_true",
        default=False,
        help="Output column profiles as JSON instead of plain text.",
    )


def profile_as_dict(result: ProfileResult) -> dict:
    """Serialise a ProfileResult to a plain dict (JSON-friendly)."""
    out = {}
    for name, p in result.columns.items():
        out[name] = {
            "count": p.count,
            "empty_count": p.empty_count,
            "fill_rate": p.fill_rate,
            "unique_values": p.unique_values,
            "min_length": p.min_length,
            "max_length": p.max_length,
            "sample_values": p.sample_values,
        }
    return out


def maybe_print_profiles(
    args: argparse.Namespace,
    left_rows: List[Dict[str, str]],
    right_rows: List[Dict[str, str]],
) -> None:
    """If --profile is set, compute and print profiles for both files."""
    if not getattr(args, "profile", False):
        return

    as_json = getattr(args, "profile_json", False)

    for label, rows in (("FILE1", left_rows), ("FILE2", right_rows)):
        result = profile_rows(rows)
        if as_json:
            import json
            print(json.dumps({label: profile_as_dict(result)}, indent=2))
        else:
            print(f"--- Profile: {label} ---")
            print(format_profile(result)print()
