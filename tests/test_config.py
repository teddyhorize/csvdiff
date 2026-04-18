"""Tests for csvdiff.config module."""
import json
import os
import pytest

from csvdiff.config import (
    CsvDiffConfig,
    ConfigError,
    default_config,
    load_config,
)


# ---------------------------------------------------------------------------
# default_config
# ---------------------------------------------------------------------------

def test_default_config_returns_instance():
    cfg = default_config()
    assert isinstance(cfg, CsvDiffConfig)


def test_default_config_values():
    cfg = default_config()
    assert cfg.delimiter == "auto"
    assert cfg.output_format == "text"
    assert cfg.color is True
    assert cfg.key_columns == []


# ---------------------------------------------------------------------------
# CsvDiffConfig.validate
# ---------------------------------------------------------------------------

def test_validate_invalid_format():
    cfg = CsvDiffConfig(output_format="xml")
    with pytest.raises(ConfigError, match="output_format"):
        cfg.validate()


def test_validate_row_limit_zero():
    cfg = CsvDiffConfig(row_limit=0)
    with pytest.raises(ConfigError, match="row_limit"):
        cfg.validate()


def test_validate_conflicting_columns():
    cfg = CsvDiffConfig(include_columns=["a"], ignore_columns=["b"])
    with pytest.raises(ConfigError, match="mutually exclusive"):
        cfg.validate()


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

def test_load_config_missing_file():
    with pytest.raises(ConfigError, match="not found"):
        load_config("/nonexistent/path/config.json")


def test_load_config_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json")
    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(str(p))


def test_load_config_unknown_keys(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"unknown_key": True}))
    with pytest.raises(ConfigError, match="Unknown config keys"):
        load_config(str(p))


def test_load_config_valid(tmp_path):
    data = {"output_format": "json", "key_columns": ["id"], "color": False}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(data))
    cfg = load_config(str(p))
    assert cfg.output_format == "json"
    assert cfg.key_columns == ["id"]
    assert cfg.color is False


def test_load_config_defaults_preserved(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({}))
    cfg = load_config(str(p))
    assert cfg.delimiter == "auto"
    assert cfg.row_limit is None
