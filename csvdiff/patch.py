"""Generate and apply patches to transform one CSV into another."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from csvdiff.differ import DiffResult


class PatchError(Exception):
    pass


@dataclass
class PatchOperation:
    op: str  # 'add', 'remove', 'modify'
    key: str
    row: Dict[str, Any] = field(default_factory=dict)
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Patch:
    key_column: str
    operations: List[PatchOperation] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.operations) == 0


def build_patch(diff: DiffResult, key_column: str) -> Patch:
    ops: List[PatchOperation] = []

    for key, row in diff.added_rows.items():
        ops.append(PatchOperation(op="add", key=str(key), row=row))

    for key, row in diff.removed_rows.items():
        ops.append(PatchOperation(op="remove", key=str(key), row=row))

    for key, changes in diff.modified_rows.items():
        ops.append(PatchOperation(op="modify", key=str(key), changes=changes))

    return Patch(key_column=key_column, operations=ops)


def apply_patch(rows: List[Dict[str, Any]], patch: Patch) -> List[Dict[str, Any]]:
    key = patch.key_column
    indexed = {str(r.get(key)): dict(r) for r in rows}

    for op in patch.operations:
        if op.op == "add":
            if op.key in indexed:
                raise PatchError(f"Cannot add: key '{op.key}' already exists")
            indexed[op.key] = op.row
        elif op.op == "remove":
            if op.key not in indexed:
                raise PatchError(f"Cannot remove: key '{op.key}' not found")
            del indexed[op.key]
        elif op.op == "modify":
            if op.key not in indexed:
                raise PatchError(f"Cannot modify: key '{op.key}' not found")
            for field_name, change in op.changes.items():
                indexed[op.key][field_name] = change.get("new", indexed[op.key].get(field_name))
        else:
            raise PatchError(f"Unknown operation: {op.op}")

    return list(indexed.values())


def patch_summary(patch: Patch) -> str:
    counts = {"add": 0, "remove": 0, "modify": 0}
    for op in patch.operations:
        counts[op.op] = counts.get(op.op, 0) + 1
    return (
        f"Patch: {counts['add']} additions, "
        f"{counts['remove']} removals, "
        f"{counts['modify']} modifications"
    )
