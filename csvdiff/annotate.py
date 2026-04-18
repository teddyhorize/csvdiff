"""Annotation support: attach change labels to rows for export or display."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from csvdiff.differ import DiffResult

ANNOTATION_KEY = "_diff"

ADDED_LABEL = "added"
REMOVED_LABEL = "removed"
MODIFIED_LABEL = "modified"
UNCHANGED_LABEL = "unchanged"


@dataclass
class AnnotatedRow:
    row: Dict[str, str]
    label: str
    changed_fields: List[str] = field(default_factory=list)


def annotate_diff(result: DiffResult, include_unchanged: bool = False) -> List[AnnotatedRow]:
    """Produce a flat list of AnnotatedRow from a DiffResult."""
    annotated: List[AnnotatedRow] = []

    for key, row in result.added_rows.items():
        annotated.append(AnnotatedRow(row=row, label=ADDED_LABEL))

    for key, row in result.removed_rows.items():
        annotated.append(AnnotatedRow(row=row, label=REMOVED_LABEL))

    for key, (old_row, new_row, fields) in result.modified_rows.items():
        annotated.append(AnnotatedRow(row=new_row, label=MODIFIED_LABEL, changed_fields=fields))

    if include_unchanged:
        for key, row in result.unchanged_rows.items():
            annotated.append(AnnotatedRow(row=row, label=UNCHANGED_LABEL))

    return annotated


def to_flat_dicts(annotated_rows: List[AnnotatedRow], annotation_key: str = ANNOTATION_KEY) -> List[Dict[str, str]]:
    """Convert annotated rows to plain dicts with an annotation column."""
    result = []
    for ar in annotated_rows:
        row = dict(ar.row)
        row[annotation_key] = ar.label
        result.append(row)
    return result


def format_annotation(ar: AnnotatedRow, color: bool = False) -> str:
    """Return a short human-readable string describing the annotated row."""
    label = ar.label.upper()
    key_hint = list(ar.row.values())[:1]
    hint = key_hint[0] if key_hint else "?"
    suffix = ""
    if ar.changed_fields:
        suffix = f" [{', '.join(ar.changed_fields)}]"
    if color:
        colors = {ADDED_LABEL: "\033[32m", REMOVED_LABEL: "\033[31m", MODIFIED_LABEL: "\033[33m", UNCHANGED_LABEL: "\033[0m"}
        reset = "\033[0m"
        c = colors.get(ar.label, "")
        return f"{c}[{label}]{reset} {hint}{suffix}"
    return f"[{label}] {hint}{suffix}"
