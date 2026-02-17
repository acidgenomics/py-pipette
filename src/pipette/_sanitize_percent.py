"""Sanitize percent strings to numeric values."""

from typing import Any

import pandas as pd


def sanitize_percent(x: Any) -> Any:
    """Convert percent strings to numeric fractions.

    Parameters
    ----------
    x : pd.DataFrame or pd.Series
        Input data containing percent strings (e.g. "50%").

    Returns
    -------
    Same type as input with percent strings converted to floats.
    """
    if isinstance(x, pd.DataFrame):
        return x.apply(_sanitize_percent_series)
    if isinstance(x, pd.Series):
        return _sanitize_percent_series(x)
    return x


def _is_string_dtype(s: pd.Series) -> bool:
    """Check if Series has string-like dtype."""
    return pd.api.types.is_string_dtype(s) or s.dtype == object


def _sanitize_percent_series(s: pd.Series) -> pd.Series:
    """Convert percent strings in a Series to numeric values."""
    if not _is_string_dtype(s):
        return s
    str_vals = s.astype(str)
    mask = str_vals.str.match(r"^[\d.]+%$", na=False)
    if not mask.any():
        return s
    # Build new series with mixed types (object dtype).
    result = s.astype(object).copy()
    pct_vals = str_vals[mask].str.rstrip("%").astype(float) / 100.0
    result.loc[mask] = pct_vals
    return result
