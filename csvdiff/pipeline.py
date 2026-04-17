"""Pipeline that wires parsing, filtering, and diffing together."""
from dataclasses import dataclass, field
from typing import List, Optional
from csvdiff.parser import load_csv
from csvdiff.filter import FilterOptions, apply_filters
from csvdiff.differ import DiffResult, diff_csv


@dataclass
class PipelineResult:
    diff_result: DiffResult
    headers_a: List[str]
    headers_b: List[str]
    row_count_a: int
    row_count_b: int


def run_pipeline(
    path_a: str,
    path_b: str,
    key: Optional[str] = None,
    filter_options: Optional[FilterOptions] = None,
) -> PipelineResult:
    """Load, filter, and diff two CSV files."""
    rows_a, headers_a = load_csv(path_a)
    rows_b, headers_b = load_csv(path_b)

    if filter_options:
        rows_a = apply_filters(rows_a, headers_a, filter_options)
        rows_b = apply_filters(rows_b, headers_b, filter_options)

    diff_result = diff_csv(rows_a, rows_b, key=key)

    return PipelineResult(
        diff_result=diff_result,
        headers_a=headers_a,
        headers_b=headers_b,
        row_count_a=len(rows_a),
        row_count_b=len(rows_b),
    )
