"""Convert columns to categorical (factor) type."""

from typing import Any

import pandas as pd


def _is_string_dtype(s: pd.Series) -> bool:
    """Check if Series has string-like dtype."""
    return pd.api.types.is_string_dtype(s) or s.dtype == object


def factorize(x: Any) -> Any:
    """Convert columns with non-unique values to categorical.

    Parameters
    ----------
    x : pd.DataFrame or pd.Series
        Input data.

    Returns
    -------
    Same type as input with eligible columns converted to Categorical.
    """
    if isinstance(x, pd.DataFrame):
        result = x.copy()
        for col in result.columns:
            s = result[col]
            if _is_string_dtype(s) and not s.is_unique and len(s) > 0:
                result[col] = pd.Categorical(s)
        return result
    if isinstance(x, pd.Series):
        if _is_string_dtype(x) and not x.is_unique and len(x) > 0:
            return pd.Categorical(x)
        return x
    return x
