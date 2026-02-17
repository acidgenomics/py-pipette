"""Convert categorical columns back to atomic types."""

from typing import Any

import pandas as pd


def unfactorize(x: Any) -> Any:
    """Convert categorical columns back to their underlying type.

    Parameters
    ----------
    x : pd.DataFrame or pd.Series
        Input data.

    Returns
    -------
    Same type as input with categorical columns converted back.
    """
    if isinstance(x, pd.DataFrame):
        result = x.copy()
        for col in result.columns:
            if isinstance(result[col].dtype, pd.CategoricalDtype):
                result[col] = result[col].astype(result[col].cat.categories.dtype)
        return result
    if isinstance(x, pd.Series):
        if isinstance(x.dtype, pd.CategoricalDtype):
            return x.astype(x.cat.categories.dtype)
        return x
    return x
