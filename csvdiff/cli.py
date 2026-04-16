"""Command-line interface for csvdiff."""

import argparse
import sys

from csvdiff.parser import load_csv, CSVParseError
from csvdiff.differ import diff_csv, has_differences
from csvdiff.formatter import format_diff, FormatOptions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff",
        description="Compare and highlight structural differences between CSV files.",
    )
    parser.add_argument("file_a", help="Original CSV file")
    parser.add_argument("file_b", help="Modified CSV file")
    parser.add_argument("-k", "--key", default="id", help="Column to use as row key (default: id)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--compact", action="store_true", help="Show summary counts only")
    parser.add_argument("--no-summary", action="store_true", help="Hide summary line")
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = load_csv(args.file_a)
        rows_b = load_csv(args.file_b)
    except CSVParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = diff_csv(rows_a, rows_b, key=args.key)

    options = FormatOptions(
        color=not args.no_color,
        show_summary=not args.no_summary,
        compact=args.compact,
    )

    print(format_diff(result, options))

    if args.exit_code and has_differences(result):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
