"""Tests for encode, decode, and droplevels."""

import pandas as pd
import pytest

from pipette import decode, droplevels, encode


def _is_string_like(dtype: object) -> bool:
    """Return True for object or StringDtype (pandas 3.x)."""
    return dtype is object or isinstance(dtype, pd.StringDtype)


class TestEncode:
    """Tests for encode()."""

    def test_encodes_object_columns_with_duplicates(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": [1, 2, 3]})
        result = encode(df)
        assert isinstance(result["a"].dtype, pd.CategoricalDtype)
        assert result["b"].dtype == df["b"].dtype

    def test_skips_unique_columns(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "z"]})
        result = encode(df)
        assert not isinstance(result["a"].dtype, pd.CategoricalDtype)

    def test_j_parameter_targets_specific_columns(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": ["p", "q", "p"]})
        result = encode(df, j=["a"])
        assert isinstance(result["a"].dtype, pd.CategoricalDtype)
        assert not isinstance(result["b"].dtype, pd.CategoricalDtype)

    def test_j_missing_column_raises(self) -> None:
        df = pd.DataFrame({"a": ["x", "y"]})
        with pytest.raises(ValueError, match="Columns not found"):
            encode(df, j=["z"])

    def test_returns_copy(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"]})
        result = encode(df)
        assert result is not df


class TestDecode:
    """Tests for decode()."""

    def test_roundtrip_with_encode(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": [1, 2, 3]})
        encoded = encode(df)
        decoded = decode(encoded)
        assert _is_string_like(decoded["a"].dtype)
        assert list(decoded["a"]) == list(df["a"])

    def test_j_parameter_targets_specific_columns(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "x"], "b": ["p", "q", "p"]})
        encoded = encode(df)
        decoded = decode(encoded, j=["a"])
        assert _is_string_like(decoded["a"].dtype)
        assert isinstance(decoded["b"].dtype, pd.CategoricalDtype)

    def test_j_missing_column_raises(self) -> None:
        df = pd.DataFrame({"a": ["x", "y"]})
        with pytest.raises(ValueError, match="Columns not found"):
            decode(df, j=["z"])

    def test_skips_non_categorical(self) -> None:
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = decode(df)
        assert result["a"].dtype == df["a"].dtype


class TestDroplevels:
    """Tests for droplevels()."""

    def test_removes_unused_categories(self) -> None:
        df = pd.DataFrame({"a": pd.Categorical(["x", "y"], categories=["x", "y", "z"])})
        result = droplevels(df)
        assert list(result["a"].cat.categories) == ["x", "y"]

    def test_j_parameter_targets_specific_columns(self) -> None:
        df = pd.DataFrame(
            {
                "a": pd.Categorical(["x"], categories=["x", "y"]),
                "b": pd.Categorical(["p"], categories=["p", "q"]),
            }
        )
        result = droplevels(df, j=["a"])
        assert list(result["a"].cat.categories) == ["x"]
        assert list(result["b"].cat.categories) == ["p", "q"]

    def test_j_missing_column_raises(self) -> None:
        df = pd.DataFrame({"a": pd.Categorical(["x"])})
        with pytest.raises(ValueError, match="Columns not found"):
            droplevels(df, j=["z"])

    def test_returns_copy(self) -> None:
        df = pd.DataFrame({"a": pd.Categorical(["x"], categories=["x", "y"])})
        result = droplevels(df)
        assert result is not df
