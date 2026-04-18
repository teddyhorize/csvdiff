"""CSV lint checks: detect common structural issues in a CSV dataset."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


class LintError(Exception):
    pass


@dataclass
class LintIssue:
    row: int
    column: str
    code: str
    message: str


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.issues) == 0


def _check_empty_cells(rows: List[Dict[str, Any]], columns: List[str]) -> List[LintIssue]:
    issues = []
    for i, row in enumerate(rows):
        for col in columns:
            val = row.get(col, "")
            if val is None or str(val).strip() == "":
                issues.append(LintIssue(row=i, column=col, code="EMPTY_CELL",
                                        message=f"Empty value in column '{col}' at row {i}"))
    return issues


def _check_duplicate_keys(rows: List[Dict[str, Any]], key_column: str) -> List[LintIssue]:
    seen: Dict[str, int] = {}
    issues = []
    for i, row in enumerate(rows):
        val = str(row.get(key_column, ""))
        if val in seen:
            issues.append(LintIssue(row=i, column=key_column, code="DUPLICATE_KEY",
                                    message=f"Duplicate key '{val}' in column '{key_column}' at row {i} (first seen at row {seen[val]})"))
        else:
            seen[val] = i
    return issues


def _check_type_consistency(rows: List[Dict[str, Any]], columns: List[str]) -> List[LintIssue]:
    issues = []
    for col in columns:
        numeric_rows = []
        for i, row in enumerate(rows):
            val = str(row.get(col, "")).strip()
            if val == "":
                continue
            try:
                float(val)
                numeric_rows.append((i, True))
            except ValueError:
                numeric_rows.append((i, False))
        types = [t for _, t in numeric_rows]
        if types and any(t != types[0] for t in types):
            for i, is_num in numeric_rows:
                if not is_num:
                    issues.append(LintIssue(row=i, column=col, code="TYPE_MISMATCH",
                                            message=f"Non-numeric value in mostly-numeric column '{col}' at row {i}"))
    return issues


def lint_rows(rows: List[Dict[str, Any]], columns: List[str],
              key_column: str = None, check_types: bool = True) -> LintResult:
    if not rows:
        return LintResult()
    issues: List[LintIssue] = []
    issues.extend(_check_empty_cells(rows, columns))
    if key_column:
        issues.extend(_check_duplicate_keys(rows, key_column))
    if check_types:
        issues.extend(_check_type_consistency(rows, columns))
    return LintResult(issues=issues)


def format_lint(result: LintResult) -> str:
    if result.is_clean():
        return "No lint issues found."
    lines = [f"Found {len(result.issues)} lint issue(s):"]
    for issue in result.issues:
        lines.append(f"  [{issue.code}] row={issue.row} col={issue.column}: {issue.message}")
    return "\n".join(lines)
