"""Convert columns to and from pandas Categorical."""

from typing import cast

import pandas as pd


def _is_string_dtype(s: pd.Series) -> bool:
    """Check if a Series has string-like dtype."""
    return pd.api.types.is_string_dtype(s) or s.dtype == object


def categorize(
    x: pd.DataFrame | pd.Series,
    *,
    columns: list[str] | None = None,
) -> pd.DataFrame | pd.Series:
    """Convert columns to ``Categorical``.

    Parameters
    ----------
    x : pd.DataFrame or pd.Series
        Input data.
    columns : list of str, optional
        Column names to convert. Only valid for a DataFrame. If ``None``
        on a DataFrame, converts every string-like column that contains
        duplicate values. Required to be ``None`` for a Series.

    Returns
    -------
    pd.DataFrame or pd.Series
        Same type as input, with the selected columns (or the Series
        itself) converted to ``Categorical``.
    """
    if isinstance(x, pd.DataFrame):
        result = x.copy()
        if columns is None:
            cols = [
                c
                for c in result.columns
                if _is_string_dtype(cast(pd.Series, result[c]))
                and cast(pd.Series, result[c]).duplicated().any()
            ]
        else:
            missing = [c for c in columns if c not in result.columns]
            if missing:
                msg = f"Columns not found: {missing!r}"
                raise ValueError(msg)
            cols = columns
        for col in cols:
            result[col] = result[col].astype("category")
        return result
    if isinstance(x, pd.Series):
        if columns is not None:
            msg = "columns is only valid for a DataFrame."
            raise ValueError(msg)
        if _is_string_dtype(x) and not x.is_unique and len(x) > 0:
            return pd.Series(pd.Categorical(x), index=x.index, name=x.name)
        return x
    return x


def uncategorize(
    x: pd.DataFrame | pd.Series,
    *,
    columns: list[str] | None = None,
) -> pd.DataFrame | pd.Series:
    """Convert ``Categorical`` columns back to their underlying dtype.

    Parameters
    ----------
    x : pd.DataFrame or pd.Series
        Input data.
    columns : list of str, optional
        Column names to convert. Only valid for a DataFrame. If ``None``
        on a DataFrame, converts every ``Categorical`` column. Required
        to be ``None`` for a Series.

    Returns
    -------
    pd.DataFrame or pd.Series
        Same type as input, with the selected ``Categorical`` columns
        (or the Series itself) converted back to their underlying dtype.
    """
    if isinstance(x, pd.DataFrame):
        result = x.copy()
        if columns is None:
            cols = [c for c in result.columns if isinstance(result[c].dtype, pd.CategoricalDtype)]
        else:
            missing = [c for c in columns if c not in result.columns]
            if missing:
                msg = f"Columns not found: {missing!r}"
                raise ValueError(msg)
            cols = [c for c in columns if isinstance(result[c].dtype, pd.CategoricalDtype)]
        for col in cols:
            result[col] = result[col].astype(result[col].cat.categories.dtype)
        return result
    if isinstance(x, pd.Series):
        if columns is not None:
            msg = "columns is only valid for a DataFrame."
            raise ValueError(msg)
        if isinstance(x.dtype, pd.CategoricalDtype):
            return x.astype(x.cat.categories.dtype)
        return x
    return x
