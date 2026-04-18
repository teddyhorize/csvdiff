"""Configuration loading and validation for csvdiff."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


class ConfigError(Exception):
    pass


@dataclass
class CsvDiffConfig:
    delimiter: str = "auto"
    key_columns: List[str] = field(default_factory=list)
    ignore_columns: List[str] = field(default_factory=list)
    include_columns: List[str] = field(default_factory=list)
    row_limit: Optional[int] = None
    output_format: str = "text"  # text | json | csv | markdown
    color: bool = True
    show_schema: bool = True

    def validate(self) -> None:
        valid_formats = {"text", "json", "csv", "markdown"}
        if self.output_format not in valid_formats:
            raise ConfigError(
                f"Invalid output_format '{self.output_format}'. "
                f"Must be one of: {', '.join(sorted(valid_formats))}"
            )
        if self.row_limit is not None and self.row_limit < 1:
            raise ConfigError("row_limit must be a positive integer.")
        if self.include_columns and self.ignore_columns:
            raise ConfigError(
                "include_columns and ignore_columns are mutually exclusive."
            )


def load_config(path: str) -> CsvDiffConfig:
    """Load a JSON config file and return a CsvDiffConfig."""
    if not os.path.exists(path):
        raise ConfigError(f"Config file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config file: {exc}") from exc

    allowed = CsvDiffConfig.__dataclass_fields__.keys()
    unknown = set(data) - set(allowed)
    if unknown:
        raise ConfigError(f"Unknown config keys: {', '.join(sorted(unknown))}")

    cfg = CsvDiffConfig(**{k: v for k, v in data.items() if k in allowed})
    cfg.validate()
    return cfg


def default_config() -> CsvDiffConfig:
    cfg = CsvDiffConfig()
    cfg.validate()
    return cfg
