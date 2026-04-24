"""Header mapping: build a fuzzy or exact mapping between two sets of headers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class HeaderMapError(Exception):
    """Raised when header mapping fails."""


@dataclass
class HeaderMapping:
    """Result of mapping headers from one CSV to another."""
    exact: Dict[str, str] = field(default_factory=dict)   # left -> right
    fuzzy: Dict[str, str] = field(default_factory=dict)   # left -> right (case-insensitive)
    unmapped_left: List[str] = field(default_factory=list)
    unmapped_right: List[str] = field(default_factory=list)


def _normalize(name: str) -> str:
    """Normalize a header name for fuzzy matching."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def build_header_mapping(
    left: List[str],
    right: List[str],
    fuzzy: bool = True,
) -> HeaderMapping:
    """Map headers from *left* to *right*.

    Exact matches are recorded first; if *fuzzy* is True, remaining headers
    are matched case-insensitively after stripping whitespace and normalizing
    separators.
    """
    if not isinstance(left, list) or not isinstance(right, list):
        raise HeaderMapError("Headers must be lists of strings.")

    result = HeaderMapping()
    right_remaining: Dict[str, str] = {h: h for h in right}  # right_name -> right_name

    # Exact pass
    for lh in left:
        if lh in right_remaining:
            result.exact[lh] = right_remaining.pop(lh)
        else:
            result.unmapped_left.append(lh)

    if not fuzzy:
        result.unmapped_right = list(right_remaining.keys())
        return result

    # Fuzzy pass on remaining
    norm_right: Dict[str, str] = {_normalize(rh): rh for rh in right_remaining}
    still_unmapped: List[str] = []

    for lh in result.unmapped_left:
        key = _normalize(lh)
        if key in norm_right:
            matched_right = norm_right.pop(key)
            result.fuzzy[lh] = matched_right
        else:
            still_unmapped.append(lh)

    result.unmapped_left = still_unmapped
    result.unmapped_right = list(norm_right.values())
    return result


def format_header_mapping(mapping: HeaderMapping) -> str:
    """Return a human-readable summary of the header mapping."""
    lines: List[str] = []
    if mapping.exact:
        lines.append("Exact matches:")
        for l, r in mapping.exact.items():
            lines.append(f"  {l!r} -> {r!r}")
    if mapping.fuzzy:
        lines.append("Fuzzy matches:")
        for l, r in mapping.fuzzy.items():
            lines.append(f"  {l!r} ~> {r!r}")
    if mapping.unmapped_left:
        lines.append("Unmapped (left): " + ", ".join(repr(h) for h in mapping.unmapped_left))
    if mapping.unmapped_right:
        lines.append("Unmapped (right): " + ", ".join(repr(h) for h in mapping.unmapped_right))
    return "\n".join(lines) if lines else "No headers to map."
