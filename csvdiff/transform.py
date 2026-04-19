"""Column value transformation (find/replace, regex substitution)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class TransformError(Exception):
    pass


@dataclass
class TransformRule:
    column: str
    pattern: str
    replacement: str
    use_regex: bool = False
    _compiled: Optional[re.Pattern] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.use_regex:
            try:
                self._compiled = re.compile(self.pattern)
            except re.error as exc:
                raise TransformError(f"Invalid regex {self.pattern!r}: {exc}") from exc


@dataclass
class TransformOptions:
    rules: List[TransformRule] = field(default_factory=list)


def _apply_rule(value: str, rule: TransformRule) -> str:
    if rule.use_regex and rule._compiled is not None:
        return rule._compiled.sub(rule.replacement, value)
    return value.replace(rule.pattern, rule.replacement)


def transform_row(
    row: Dict[str, str],
    options: TransformOptions,
) -> Dict[str, str]:
    result = dict(row)
    for rule in options.rules:
        if rule.column in result:
            result[rule.column] = _apply_rule(result[rule.column], rule)
    return result


def transform_rows(
    rows: List[Dict[str, str]],
    options: TransformOptions,
) -> List[Dict[str, str]]:
    if not options.rules:
        return rows
    return [transform_row(r, options) for r in rows]


def transform_pair(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    options: TransformOptions,
) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    return transform_rows(left, options), transform_rows(right, options)
