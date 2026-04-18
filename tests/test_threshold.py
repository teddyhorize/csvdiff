import pytest
from csvdiff.differ import DiffResult
from csvdiff.threshold import ThresholdOptions, check_threshold, format_threshold_warning


@pytest.fixture
def result():
    return DiffResult(
        added=[{"id": "3", "name": "C"}],
        removed=[{"id": "1", "name": "A"}],
        modified=[("2", {"id": "2", "name": "B"}, {"id": "2", "name": "B2"})],
        added_columns=[],
        removed_columns=[],
    )


def test_check_threshold_all_none(result):
    opts = ThresholdOptions()
    assert check_threshold(result, opts) is True


def test_check_threshold_added_within(result):
    opts = ThresholdOptions(max_added=2)
    assert check_threshold(result, opts) is True


def test_check_threshold_added_exceeded(result):
    opts = ThresholdOptions(max_added=0)
    assert check_threshold(result, opts) is False


def test_check_threshold_removed_exceeded(result):
    opts = ThresholdOptions(max_removed=0)
    assert check_threshold(result, opts) is False


def test_check_threshold_modified_exceeded(result):
    opts = ThresholdOptions(max_modified=0)
    assert check_threshold(result, opts) is False


def test_check_threshold_total_exceeded(result):
    opts = ThresholdOptions(max_total=2)
    assert check_threshold(result, opts) is False


def test_check_threshold_total_within(result):
    opts = ThresholdOptions(max_total=3)
    assert check_threshold(result, opts) is True


def test_check_threshold_added_pct_exceeded(result):
    # 1 added out of 10 total = 10%, threshold 5%
    opts = ThresholdOptions(max_added_pct=5.0)
    assert check_threshold(result, opts, total_rows=10) is False


def test_check_threshold_added_pct_within(result):
    opts = ThresholdOptions(max_added_pct=20.0)
    assert check_threshold(result, opts, total_rows=10) is True


def test_check_threshold_pct_ignored_when_total_zero(result):
    opts = ThresholdOptions(max_added_pct=0.0)
    assert check_threshold(result, opts, total_rows=0) is True


def test_format_threshold_warning_contains_label(result):
    opts = ThresholdOptions(max_added=0)
    msg = format_threshold_warning(result, opts)
    assert "added rows" in msg
    assert "0" in msg


def test_format_threshold_warning_multiple(result):
    opts = ThresholdOptions(max_added=0, max_removed=0)
    msg = format_threshold_warning(result, opts)
    assert "added rows" in msg
    assert "removed rows" in msg
