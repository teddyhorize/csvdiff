"""Aggregate pipeline results into a final report."""
from dataclasses import dataclass, field
from typing import Optional
from csvdiff.pipeline import PipelineResult
from csvdiff.summary import DiffSummary, summarize, format_summary
from csvdiff.schema import SchemaDiff, compare_schemas, format_schema_diff
from csvdiff.formatter import FormatOptions, format_diff


@dataclass
class Report:
    summary: DiffSummary
    schema_diff: SchemaDiff
    diff_text: str
    schema_text: str
    summary_text: str
    is_clean: bool


def build_report(
    result: PipelineResult,
    fmt_options: Optional[FormatOptions] = None,
) -> Report:
    """Build a complete report from a pipeline result."""
    if fmt_options is None:
        fmt_options = FormatOptions()

    diff_result = result.diff_result
    summary = summarize(diff_result)
    schema_diff = compare_schemas(
        result.headers_a,
        result.headers_b,
    )

    diff_text = format_diff(diff_result, fmt_options)
    schema_text = format_schema_diff(schema_diff)
    summary_text = format_summary(summary)

    return Report(
        summary=summary,
        schema_diff=schema_diff,
        diff_text=diff_text,
        schema_text=schema_text,
        summary_text=summary_text,
        is_clean=summary.is_clean and not schema_diff.has_changes,
    )


def render_report(report: Report, verbose: bool = False) -> str:
    """Render a report to a printable string."""
    parts = []
    if report.schema_diff.has_changes:
        parts.append(report.schema_text)
    parts.append(report.diff_text)
    if verbose:
        parts.append(report.summary_text)
    return "\n".join(filter(None, parts))
