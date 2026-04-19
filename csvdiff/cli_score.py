"""CLI helpers for similarity scoring."""
from __future__ import annotations
import argparse
import json
from csvdiff.score import SimilarityScore, compute_score, format_score
from csvdiff.differ import DiffResult


def register_score_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("scoring")
    grp.add_argument(
        "--score",
        action="store_true",
        default=False,
        help="Print similarity score between the two files.",
    )
    grp.add_argument(
        "--score-json",
        action="store_true",
        default=False,
        help="Output similarity score as JSON.",
    )


def score_as_dict(s: SimilarityScore) -> dict:
    return {
        "score": s.score,
        "total_rows": s.total_rows,
        "matched_rows": s.matched_rows,
        "added": s.added,
        "removed": s.removed,
        "modified": s.modified,
    }


def maybe_print_score(args: argparse.Namespace, result: DiffResult) -> None:
    if not (getattr(args, "score", False) or getattr(args, "score_json", False)):
        return
    s = compute_score(result)
    if getattr(args, "score_json", False):
        print(json.dumps(score_as_dict(s), indent=2))
    else:
        print(format_score(s))
