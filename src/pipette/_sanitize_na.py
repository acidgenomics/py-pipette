"""Sanitize NA values in data structures."""

from typing import Any

import numpy as np
import pandas as pd

from pipette._globals import NA_STRINGS


def sanitize_na(x: Any, na_strings: list[str] | None = None) -> Any:
    """Replace NA-like strings with NaN.

    Parameters
    ----------
    x : pd.DataFrame, pd.Series, or list
        Input data.
    na_strings : list of str, optional
        Strings to treat as NA. Defaults to ``NA_STRINGS``.

    Returns
    -------
    Same type as input with NA strings replaced by NaN.
    """
    if na_strings is None:
        na_strings = NA_STRINGS
    na_set = set(na_strings)
    if isinstance(x, pd.DataFrame):
        return x.apply(lambda col: _sanitize_series(col, na_set))
    if isinstance(x, pd.Series):
        return _sanitize_series(x, na_set)
    if isinstance(x, list):
        return [np.nan if v in na_set else v for v in x]
    return x


def _sanitize_series(s: pd.Series, na_set: set) -> pd.Series:
    """Sanitize NA values in a Series."""
    if s.dtype == object:
        return s.where(~s.isin(na_set), other=np.nan)
    return s
