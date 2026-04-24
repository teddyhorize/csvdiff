"""CLI helpers for header mapping feature."""
from __future__ import annotations

import argparse
import json
from typing import List, Optional

from csvdiff.headermap import HeaderMapping, build_header_mapping, format_header_mapping


def register_headermap_args(parser: argparse.ArgumentParser) -> None:
    """Add header-mapping flags to *parser*."""
    parser.add_argument(
        "--show-header-map",
        action="store_true",
        default=False,
        help="Print a mapping of headers between the two CSV files.",
    )
    parser.add_argument(
        "--no-fuzzy-headers",
        action="store_true",
        default=False,
        help="Disable fuzzy (case-insensitive) header matching.",
    )
    parser.add_argument(
        "--header-map-json",
        action="store_true",
        default=False,
        help="Output header mapping as JSON instead of plain text.",
    )


def headermap_as_dict(mapping: HeaderMapping) -> dict:
    """Serialize *mapping* to a plain dict suitable for JSON output."""
    return {
        "exact": mapping.exact,
        "fuzzy": mapping.fuzzy,
        "unmapped_left": mapping.unmapped_left,
        "unmapped_right": mapping.unmapped_right,
    }


def maybe_print_header_map(
    args: argparse.Namespace,
    left_headers: List[str],
    right_headers: List[str],
) -> Optional[HeaderMapping]:
    """If ``--show-header-map`` is set, build and print the mapping.

    Returns the :class:`HeaderMapping` if printed, otherwise ``None``.
    """
    if not getattr(args, "show_header_map", False):
        return None

    fuzzy = not getattr(args, "no_fuzzy_headers", False)
    mapping = build_header_mapping(left_headers, right_headers, fuzzy=fuzzy)

    if getattr(args, "header_map_json", False):
        print(json.dumps(headermap_as_dict(mapping), indent=2))
    else:
        print(format_header_mapping(mapping))

    return mapping
