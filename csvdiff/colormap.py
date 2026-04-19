from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

ANSI_RESET = "\033[0m"

DEFAULT_COLORS: Dict[str, str] = {
    "added": "\033[32m",
    "removed": "\033[31m",
    "modified": "\033[33m",
    "unchanged": "\033[0m",
    "header": "\033[1;36m",
}

VALID_LABELS = set(DEFAULT_COLORS.keys())


class ColormapError(Exception):
    pass


@dataclass
class Colormap:
    colors: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_COLORS))

    def get(self, label: str) -> str:
        return self.colors.get(label, ANSI_RESET)

    def apply(self, label: str, text: str) -> str:
        return f"{self.get(label)}{text}{ANSI_RESET}"


def default_colormap() -> Colormap:
    return Colormap(colors=dict(DEFAULT_COLORS))


def build_colormap(overrides: Dict[str, str]) -> Colormap:
    invalid = set(overrides) - VALID_LABELS
    if invalid:
        raise ColormapError(f"Unknown color labels: {sorted(invalid)}")
    colors = dict(DEFAULT_COLORS)
    colors.update(overrides)
    return Colormap(colors=colors)


def format_colormap_legend(colormap: Colormap) -> List[str]:
    lines = []
    for label in sorted(VALID_LABELS):
        sample = colormap.apply(label, label)
        lines.append(f"  {sample}")
    return lines
