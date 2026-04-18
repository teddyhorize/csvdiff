"""Merge CLI arguments and config file values into a unified CsvDiffConfig."""

from typing import Any, Dict
from csvdiff.config import CsvDiffConfig, default_config, validate


def merge_config(base: CsvDiffConfig, overrides: Dict[str, Any]) -> CsvDiffConfig:
    """Apply a dict of overrides onto a base config, returning a new instance.

    Only keys present in the overrides dict with non-None values are applied.
    The resulting config is validated before being returned.
    """
    merged = CsvDiffConfig(
        delimiter=overrides.get("delimiter") or base.delimiter,
        key_column=overrides.get("key_column") or base.key_column,
        output_format=overrides.get("output_format") or base.output_format,
        include_columns=overrides.get("include_columns") or base.include_columns,
        exclude_columns=overrides.get("exclude_columns") or base.exclude_columns,
        row_limit=overrides.get("row_limit") if overrides.get("row_limit") is not None else base.row_limit,
        color=overrides.get("color") if overrides.get("color") is not None else base.color,
        use_cache=overrides.get("use_cache") if overrides.get("use_cache") is not None else base.use_cache,
    )
    validate(merged)
    return merged


def merge_from_cli(config: CsvDiffConfig, args: Any) -> CsvDiffConfig:
    """Build overrides dict from an argparse Namespace and merge with config."""
    overrides: Dict[str, Any] = {}
    for field in CsvDiffConfig.__dataclass_fields__:  # type: ignore[attr-defined]
        val = getattr(args, field, None)
        if val is not None:
            overrides[field] = val
    return merge_config(config, overrides)
