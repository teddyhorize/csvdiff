"""CLI helpers for the timeline feature."""
from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace
from typing import Optional

from csvdiff.timeline import Timeline, format_timeline


def register_timeline_args(parser: ArgumentParser) -> None:
    """Add timeline-related flags to *parser*."""
    grp = parser.add_argument_group("timeline")
    grp.add_argument(
        "--timeline",
        action="store_true",
        default=False,
        help="Print a chronological summary of all diff runs in this session.",
    )
    grp.add_argument(
        "--timeline-label",
        metavar="LABEL",
        default="",
        help="Label to attach to the current run in the timeline.",
    )
    grp.add_argument(
        "--timeline-json",
        action="store_true",
        default=False,
        help="Emit timeline as JSON instead of plain text.",
    )


def timeline_as_dict(timeline: Timeline) -> dict:
    """Serialise *timeline* to a plain dict suitable for JSON output."""
    return {
        "entries": [
            {
                "timestamp": e.timestamp,
                "label": e.label,
                "added": e.added,
                "removed": e.removed,
                "modified": e.modified,
                "added_columns": e.added_columns,
                "removed_columns": e.removed_columns,
                "total_changes": e.total_changes,
                "is_clean": e.is_clean,
            }
            for e in timeline.entries
        ]
    }


def maybe_print_timeline(
    args: Namespace,
    timeline: Timeline,
    *,
    color: bool = False,
) -> None:
    """Print the timeline if the --timeline flag was supplied."""
    if not getattr(args, "timeline", False):
        return
    if getattr(args, "timeline_json", False):
        print(json.dumps(timeline_as_dict(timeline), indent=2))
    else:
        print(format_timeline(timeline, color=color))
