"""Standalone CLI command: csvdiff-split — split a diff result into per-type CSVs."""

from __future__ import annotations

import argparse
import sys

from csvdiff.parser import load_csv, CSVParseError
from csvdiff.differ import diff_csv
from csvdiff.split import SplitOptions, split_diff, format_split_result


def build_split_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff-split",
        description="Compare two CSV files and write each change type to its own file.",
    )
    p.add_argument("file_a", help="Original CSV file.")
    p.add_argument("file_b", help="Updated CSV file.")
    p.add_argument(
        "--key",
        metavar="COLUMN",
        default=None,
        help="Column to use as row key for matching.",
    )
    p.add_argument(
        "--output-dir",
        metavar="DIR",
        default=".",
        help="Directory to write output files (default: current directory).",
    )
    p.add_argument(
        "--prefix",
        metavar="PREFIX",
        default="diff",
        help="Filename prefix for output files (default: diff).",
    )
    p.add_argument(
        "--include-unchanged",
        action="store_true",
        default=False,
        help="Also write unchanged rows to a separate file.",
    )
    return p


def main(argv=None) -> int:
    parser = build_split_parser()
    args = parser.parse_args(argv)

    try:
        rows_a, headers_a = load_csv(args.file_a)
        rows_b, headers_b = load_csv(args.file_b)
    except CSVParseError as exc:
        print(f"Error reading CSV: {exc}", file=sys.stderr)
        return 1

    headers = headers_a
    result = diff_csv(rows_a, rows_b, key_column=args.key)

    opts = SplitOptions(
        output_dir=args.output_dir,
        prefix=args.prefix,
        include_unchanged=args.include_unchanged,
    )

    split_result = split_diff(result, headers, opts)
    print(format_split_result(split_result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
