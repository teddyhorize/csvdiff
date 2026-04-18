"""CLI integration for patch generation and application."""

import argparse
import json
from csvdiff.patch import build_patch, apply_patch, patch_summary, Patch, PatchOperation


def register_patch_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--patch", action="store_true", help="Output patch instead of diff")
    parser.add_argument("--apply-patch", metavar="FILE", help="Apply a patch file to input CSV")
    parser.add_argument("--patch-output", metavar="FILE", help="Write patch to file")


def patch_to_dict(patch: Patch) -> dict:
    return {
        "key_column": patch.key_column,
        "operations": [
            {"op": op.op, "key": op.key, "row": op.row, "changes": op.changes}
            for op in patch.operations
        ],
    }


def patch_from_dict(data: dict) -> Patch:
    ops = [
        PatchOperation(
            op=o["op"], key=o["key"],
            row=o.get("row", {}), changes=o.get("changes", {})
        )
        for o in data.get("operations", [])
    ]
    return Patch(key_column=data["key_column"], operations=ops)


def maybe_print_patch(diff, key_column: str, args: argparse.Namespace) -> bool:
    if not getattr(args, "patch", False):
        return False
    patch = build_patch(diff, key_column)
    data = patch_to_dict(patch)
    output = json.dumps(data, indent=2)
    patch_output = getattr(args, "patch_output", None)
    if patch_output:
        with open(patch_output, "w") as f:
            f.write(output)
    else:
        print(output)
    print(patch_summary(patch))
    return True
