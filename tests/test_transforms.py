"""Tests for data transformation functions."""

import pandas as pd
import pytest

from pipette._drop_nested_columns import drop_nested_columns
from pipette._match_rowname_column import _match_rowname_column
from pipette._sanitize_percent import sanitize_percent


class TestSanitizePercent:
    def test_basic_series(self) -> None:
        s = pd.Series(["50%", "25.5%", "100%"])
        result = sanitize_percent(s)
        assert result.iloc[0] == pytest.approx(0.50)
        assert result.iloc[1] == pytest.approx(0.255)
        assert result.iloc[2] == pytest.approx(1.0)

    def test_dataframe(self) -> None:
        df = pd.DataFrame({"pct": ["50%", "25%"], "value": [1, 2]})
        result = sanitize_percent(df)
        assert result["pct"].iloc[0] == pytest.approx(0.50)


class TestDropNestedColumns:
    def test_keeps_scalar(self) -> None:
        df = pd.DataFrame({"name": ["a", "b"], "value": [1, 2]})
        result = drop_nested_columns(df)
        assert list(result.columns) == ["name", "value"]

    def test_removes_list(self) -> None:
        df = pd.DataFrame(
            {
                "name": ["a", "b"],
                "tags": [["x", "y"], ["z"]],
                "value": [1, 2],
            }
        )
        result = drop_nested_columns(df)
        assert "tags" not in result.columns


class TestMatchRownameColumn:
    def test_rowname(self) -> None:
        df = pd.DataFrame({"rowname": ["a", "b", "c"], "value": [1, 2, 3]})
        assert _match_rowname_column(df) == "rowname"

    def test_rn(self) -> None:
        df = pd.DataFrame({"rn": ["a", "b", "c"], "value": [1, 2, 3]})
        assert _match_rowname_column(df) == "rn"

    def test_no_match(self) -> None:
        df = pd.DataFrame({"col1": ["a", "b"], "col2": [1, 2]})
        assert _match_rowname_column(df) is None

    def test_non_unique(self) -> None:
        df = pd.DataFrame({"rowname": ["a", "a", "c"], "value": [1, 2, 3]})
        assert _match_rowname_column(df) is None
