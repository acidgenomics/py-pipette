"""Remove NA values from data structures."""

from typing import Any

import numpy as np
import pandas as pd


def remove_na(x: Any, how: str = "all") -> Any:
    """Remove NA values from data.

    Parameters
    ----------
    x : pd.DataFrame, pd.Series, or list
        Input data.
    how : str
        For DataFrames: "row" removes all-NA rows, "col" removes all-NA
        columns, "all" removes both.

    Returns
    -------
    Data with NA values removed.
    """
    if isinstance(x, pd.DataFrame):
        df = x
        if how in ("row", "all"):
            df = df.dropna(axis=0, how="all")
        if how in ("col", "all"):
            df = df.dropna(axis=1, how="all")
        return df
    if isinstance(x, pd.Series):
        return x.dropna()
    if isinstance(x, list):
        return [
            v for v in x if v is not None and not (isinstance(v, float) and np.isnan(v))
        ]
    return x
