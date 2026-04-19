"""Column rename support for csvdiff."""
from dataclasses import dataclass, field
from typing import Dict, List


class RenameError(Exception):
    pass


@dataclass
class RenameOptions:
    mapping: Dict[str, str] = field(default_factory=dict)  # old -> new


def _parse_rename_pair(pair: str) -> tuple:
    """Parse 'old:new' string into (old, new) tuple."""
    if ":" not in pair:
        raise RenameError(f"Invalid rename pair {pair!r}: expected 'old:new' format")
    old, _, new = pair.partition(":")
    old, new = old.strip(), new.strip()
    if not old or not new:
        raise RenameError(f"Invalid rename pair {pair!r}: names must not be empty")
    return old, new


def build_rename_options(pairs: List[str]) -> RenameOptions:
    """Build RenameOptions from a list of 'old:new' strings."""
    mapping = {}
    for pair in pairs:
        old, new = _parse_rename_pair(pair)
        mapping[old] = new
    return RenameOptions(mapping=mapping)


def rename_headers(headers: List[str], options: RenameOptions) -> List[str]:
    """Return headers with renames applied."""
    return [options.mapping.get(h, h) for h in headers]


def rename_rows(
    rows: List[Dict[str, str]], options: RenameOptions
) -> List[Dict[str, str]]:
    """Return rows with column keys renamed."""
    if not options.mapping:
        return rows
    return [
        {options.mapping.get(k, k): v for k, v in row.items()}
        for row in rows
    ]


def apply_renames(
    rows_a: List[Dict[str, str]],
    rows_b: List[Dict[str, str]],
    options: RenameOptions,
) -> tuple:
    """Apply renames to both row sets and return updated pair."""
    return rename_rows(rows_a, options), rename_rows(rows_b, options)
