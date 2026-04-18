"""Standalone patch apply command for csvdiff."""

import argparse
import json
import sys
from csvdiff.parser import load_csv
from csvdiff.patch import apply_patch, patch_summary
from csvdiff.cli_patch import patch_from_dict


def build_apply_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvpatch",
        description="Apply a csvdiff patch file to a CSV",
    )
    p.add_argument("csv_file", help="Input CSV file to patch")
    p.add_argument("patch_file", help="Patch JSON file to apply")
    p.add_argument("--output", "-o", metavar="FILE", help="Output file (default: stdout)")
    p.add_argument("--summary", action="store_true", help="Print patch summary")
    return p


def main(argv=None) -> int:
    parser = build_apply_parser()
    args = parser.parse_args(argv)

    try:
        rows = load_csv(args.csv_file)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        return 1

    try:
        with open(args.patch_file) as f:
            patch_data = json.load(f)
        patch = patch_from_dict(patch_data)
    except Exception as e:
        print(f"Error reading patch: {e}", file=sys.stderr)
        return 1

    try:
        result = apply_patch(rows, patch)
    except Exception as e:
        print(f"Patch failed: {e}", file=sys.stderr)
        return 1

    if args.summary:
        print(patch_summary(patch), file=sys.stderr)

    if not result:
        return 0

    headers = list(result[0].keys())
    lines = [",".join(headers)]
    for row in result:
        lines.append(",".join(str(row.get(h, "")) for h in headers))
    output = "\n".join(lines) + "\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
