"""Column-level value validation for CSV rows."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re


class ValidateError(Exception):
    pass


@dataclass
class ValidationRule:
    column: str
    pattern: Optional[str] = None
    not_empty: bool = False
    numeric: bool = False


@dataclass
class ValidationIssue:
    row_index: int
    column: str
    value: str
    reason: str


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.issues) == 0


def _check_rule(rule: ValidationRule, value: str, row_index: int) -> List[ValidationIssue]:
    issues = []
    if rule.not_empty and not value.strip():
        issues.append(ValidationIssue(row_index, rule.column, value, "empty value"))
    if rule.numeric:
        try:
            float(value)
        except ValueError:
            issues.append(ValidationIssue(row_index, rule.column, value, "not numeric"))
    if rule.pattern:
        try:
            if not re.fullmatch(rule.pattern, value):
                issues.append(ValidationIssue(row_index, rule.column, value, f"does not match pattern '{rule.pattern}'"))
        except re.error as e:
            raise ValidateError(f"Invalid pattern '{rule.pattern}': {e}") from e
    return issues


def validate_rows(rows: List[Dict[str, str]], rules: List[ValidationRule]) -> ValidationResult:
    result = ValidationResult()
    for i, row in enumerate(rows):
        for rule in rules:
            value = row.get(rule.column, "")
            result.issues.extend(_check_rule(rule, value, i))
    return result


def format_validation(result: ValidationResult) -> str:
    if result.is_clean():
        return "No validation issues found."
    lines = [f"{len(result.issues)} validation issue(s):"]
    for issue in result.issues:
        lines.append(f"  row {issue.row_index}, column '{issue.column}': {issue.reason} (got: {issue.value!r})")
    return "\n".join(lines)
