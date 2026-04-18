"""Merge CLI arguments into a CsvDiffConfig, with config-file as base."""
from __future__ import annotations

import argparse
from typing import Optional

from csvdiff.config import CsvDiffConfig, default_config, load_config


def merge_config(
    args: argparse.Namespace,
    config_path: Optional[str] = None,
) -> CsvDiffConfig:
    """Return a CsvDiffConfig built from an optional file then CLI overrides.

    Priority: CLI flags > config file > built-in defaults.
    """
    cfg: CsvDiffConfig = load_config(config_path) if config_path else default_config()

    if getattr(args, "delimiter", None):
        cfg.delimiter = args.delimiter

    if getattr(args, "key", None):
        cfg.key_columns = args.key if isinstance(args.key, list) else [args.key]

    if getattr(args, "ignore", None):
        cfg.ignore_columns = args.ignore if isinstance(args.ignore, list) else [args.ignore]

    if getattr(args, "include", None):
        cfg.include_columns = args.include if isinstance(args.include, list) else [args.include]

    if getattr(args, "limit", None) is not None:
        cfg.row_limit = args.limit

    if getattr(args, "format", None):
        cfg.output_format = args.format

    if getattr(args, "no_color", False):
        cfg.color = False

    if getattr(args, "no_schema", False):
        cfg.show_schema = False

    cfg.validate()
    return cfg
