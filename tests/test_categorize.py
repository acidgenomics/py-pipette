"""Tests for categorize and uncategorize."""

import pandas as pd
import pytest

from pipette import categorize, uncategorize


def _is_string_like(dtype: object) -> bool:
    """Return True for object or StringDtype (pandas 3.x)."""
    return dtype is object or isinstance(dtype, pd.StringDtype)


class TestCategorize:
    """Tests for categorize()."""

    def test_encodes_object_columns_with_duplicates(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": [1, 2, 3]})
        result = categorize(df)
        assert isinstance(result["a"].dtype, pd.CategoricalDtype)
        assert result["b"].dtype == df["b"].dtype

    def test_skips_unique_columns(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "z"]})
        result = categorize(df)
        assert not isinstance(result["a"].dtype, pd.CategoricalDtype)

    def test_columns_parameter_targets_specific_columns(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": ["p", "q", "p"]})
        result = categorize(df, columns=["a"])
        assert isinstance(result["a"].dtype, pd.CategoricalDtype)
        assert not isinstance(result["b"].dtype, pd.CategoricalDtype)

    def test_missing_column_raises(self) -> None:
        df = pd.DataFrame({"a": ["x", "y"]})
        with pytest.raises(ValueError, match="Columns not found"):
            categorize(df, columns=["z"])

    def test_returns_copy(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"]})
        result = categorize(df)
        assert result is not df

    def test_series(self) -> None:
        s = pd.Series(["a", "b", "a", "c", "b"])
        result = categorize(s)
        assert isinstance(result.dtype, pd.CategoricalDtype)

    def test_series_rejects_columns(self) -> None:
        s = pd.Series(["a", "b", "a"])
        with pytest.raises(ValueError, match="only valid for a DataFrame"):
            categorize(s, columns=["a"])


class TestUncategorize:
    """Tests for uncategorize()."""

    def test_roundtrip_with_categorize(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": [1, 2, 3]})
        encoded = categorize(df)
        decoded = uncategorize(encoded)
        assert _is_string_like(decoded["a"].dtype)
        assert list(decoded["a"]) == list(df["a"])

    def test_columns_parameter_targets_specific_columns(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": ["p", "q", "p"]})
        encoded = categorize(df)
        decoded = uncategorize(encoded, columns=["a"])
        assert _is_string_like(decoded["a"].dtype)
        assert isinstance(decoded["b"].dtype, pd.CategoricalDtype)

    def test_missing_column_raises(self) -> None:
        df = pd.DataFrame({"a": ["x", "y"]})
        with pytest.raises(ValueError, match="Columns not found"):
            uncategorize(df, columns=["z"])

    def test_skips_non_categorical(self) -> None:
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = uncategorize(df)
        assert result["a"].dtype == df["a"].dtype

    def test_series(self) -> None:
        s = pd.Categorical(["a", "b", "a", "c", "b"])
        result = uncategorize(pd.Series(s))
        assert _is_string_like(result.dtype)
        assert list(result) == ["a", "b", "a", "c", "b"]

    def test_series_rejects_columns(self) -> None:
        s = pd.Series(pd.Categorical(["a", "b"]))
        with pytest.raises(ValueError, match="only valid for a DataFrame"):
            uncategorize(s, columns=["a"])
