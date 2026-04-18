"""Cell-level diff highlighting for changed rows."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CellDiff:
    column: str
    old_value: str
    new_value: str


@dataclass
class RowHighlight:
    key: str
    diffs: List[CellDiff] = field(default_factory=list)

    def changed_columns(self) -> List[str]:
        return [d.column for d in self.diffs]


def highlight_row(
    old_row: Dict[str, str],
    new_row: Dict[str, str],
    key: str,
) -> RowHighlight:
    """Compare two rows and return a RowHighlight with per-cell diffs."""
    columns = set(old_row) | set(new_row)
    diffs = []
    for col in sorted(columns):
        old_val = old_row.get(col, "")
        new_val = new_row.get(col, "")
        if old_val != new_val:
            diffs.append(CellDiff(column=col, old_value=old_val, new_value=new_val))
    return RowHighlight(key=key, diffs=diffs)


def highlight_modified(
    modified: Dict[str, Tuple[Dict[str, str], Dict[str, str]]]
) -> List[RowHighlight]:
    """Produce RowHighlight for every modified row in a diff result."""
    results = []
    for key, (old_row, new_row) in modified.items():
        rh = highlight_row(old_row, new_row, key)
        if rh.diffs:
            results.append(rh)
    return results


def format_highlight(highlights: List[RowHighlight], use_color: bool = True) -> str:
    """Render highlights as a human-readable string."""
    if not highlights:
        return "No cell-level differences."
    lines = []
    for rh in highlights:
        lines.append(f"Row [{rh.key}]:")
        for cd in rh.diffs:
            old = cd.old_value if cd.old_value != "" else "(empty)"
            new = cd.new_value if cd.new_value != "" else "(empty)"
            if use_color:
                lines.append(f"  {cd.column}: \033[31m{old}\033[0m -> \033[32m{new}\033[0m")
            else:
                lines.append(f"  {cd.column}: {old} -> {new}")
    return "\n".join(lines)
