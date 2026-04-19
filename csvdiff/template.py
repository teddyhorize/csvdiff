"""Template-based output rendering for diff results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import string

from csvdiff.differ import DiffResult


class TemplateError(Exception):
    pass


@dataclass
class TemplateOptions:
    template: str
    added_label: str = "ADDED"
    removed_label: str = "REMOVED"
    modified_label: str = "MODIFIED"
    separator: str = "\n"


def _safe_format(template: str, context: dict) -> str:
    try:
        return string.Formatter().vformat(template, [], context)
    except KeyError as e:
        raise TemplateError(f"Unknown template variable: {e}") from e
    except (ValueError, IndexError) as e:
        raise TemplateError(f"Invalid template: {e}") from e


def render_row(row: dict, label: str, opts: TemplateOptions) -> str:
    context = {"label": label, **row}
    return _safe_format(opts.template, context)


def render_template(result: DiffResult, opts: TemplateOptions) -> str:
    lines: list[str] = []
    for row in result.added:
        lines.append(render_row(row, opts.added_label, opts))
    for row in result.removed:
        lines.append(render_row(row, opts.removed_label, opts))
    for old, new in result.modified:
        merged = {k: new.get(k, old.get(k)) for k in set(old) | set(new)}
        lines.append(render_row(merged, opts.modified_label, opts))
    return opts.separator.join(lines)


def default_template_options(template: Optional[str] = None) -> TemplateOptions:
    tmpl = template or "[{label}] {id}"
    return TemplateOptions(template=tmpl)
