"""Tests for data transformation functions."""

import numpy as np
import pandas as pd
import pytest

from pipette._atomize import atomize
from pipette._factorize import factorize
from pipette._match_rowname_column import match_rowname_column
from pipette._metadata2 import metadata2
from pipette._remove_na import remove_na
from pipette._sanitize_percent import sanitize_percent
from pipette._unfactorize import unfactorize


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


class TestRemoveNa:
    def test_series(self) -> None:
        s = pd.Series([1, np.nan, 3, np.nan, 5])
        result = remove_na(s)
        assert len(result) == 3

    def test_dataframe_rows(self) -> None:
        df = pd.DataFrame({"col1": [1, np.nan, 3], "col2": [4, np.nan, 6]})
        result = remove_na(df, how="row")
        assert result.shape[0] == 2

    def test_dataframe_cols(self) -> None:
        df = pd.DataFrame({"col1": [1, 2], "col2": [np.nan, np.nan]})
        result = remove_na(df, how="col")
        assert result.shape[1] == 1

    def test_list(self) -> None:
        data = [1, None, 3, None, 5]
        result = remove_na(data)
        assert result == [1, 3, 5]


class TestFactorize:
    def test_basic(self) -> None:
        df = pd.DataFrame(
            {
                "group": ["a", "b", "a", "c", "b", "a"],
                "unique": ["x1", "x2", "x3", "x4", "x5", "x6"],
                "value": [1, 2, 3, 4, 5, 6],
            }
        )
        result = factorize(df)
        assert isinstance(result["group"].dtype, pd.CategoricalDtype)
        assert not isinstance(result["unique"].dtype, pd.CategoricalDtype)

    def test_series(self) -> None:
        s = pd.Series(["a", "b", "a", "c", "b"])
        result = factorize(s)
        assert isinstance(result.dtype, pd.CategoricalDtype)


class TestUnfactorize:
    def test_basic(self) -> None:
        df = pd.DataFrame(
            {
                "group": pd.Categorical(["a", "b", "a"]),
                "value": [1, 2, 3],
            }
        )
        result = unfactorize(df)
        assert not isinstance(result["group"].dtype, pd.CategoricalDtype)

    def test_roundtrip(self) -> None:
        df = pd.DataFrame({"group": ["a", "b", "a", "c", "b", "a"]})
        factorized = factorize(df)
        result = unfactorize(factorized)
        assert list(result["group"]) == list(df["group"])


class TestAtomize:
    def test_keeps_scalar(self) -> None:
        df = pd.DataFrame({"name": ["a", "b"], "value": [1, 2]})
        result = atomize(df)
        assert list(result.columns) == ["name", "value"]

    def test_removes_list(self) -> None:
        df = pd.DataFrame(
            {
                "name": ["a", "b"],
                "tags": [["x", "y"], ["z"]],
                "value": [1, 2],
            }
        )
        result = atomize(df)
        assert "tags" not in result.columns


class TestMatchRownameColumn:
    def test_rowname(self) -> None:
        df = pd.DataFrame({"rowname": ["a", "b", "c"], "value": [1, 2, 3]})
        assert match_rowname_column(df) == "rowname"

    def test_rn(self) -> None:
        df = pd.DataFrame({"rn": ["a", "b", "c"], "value": [1, 2, 3]})
        assert match_rowname_column(df) == "rn"

    def test_no_match(self) -> None:
        df = pd.DataFrame({"col1": ["a", "b"], "col2": [1, 2]})
        assert match_rowname_column(df) is None

    def test_non_unique(self) -> None:
        df = pd.DataFrame({"rowname": ["a", "a", "c"], "value": [1, 2, 3]})
        assert match_rowname_column(df) is None


class TestMetadata2:
    def test_set_and_get(self) -> None:
        df = pd.DataFrame({"col1": [1, 2, 3]})
        metadata2(df, "description", set_value="test data")
        result = metadata2(df, "description")
        assert result == "test data"

    def test_get_missing(self) -> None:
        df = pd.DataFrame({"col1": [1, 2, 3]})
        assert metadata2(df, "nonexistent") is None
