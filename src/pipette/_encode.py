"""Encode DataFrame columns to Categorical type."""

import pandas as pd


def encode(x: pd.DataFrame, *, j: list[str] | None = None) -> pd.DataFrame:
    """Encode columns as Categorical.

    Parameters
    ----------
    x : pd.DataFrame
        Input DataFrame.
    j : list of str, optional
        Column names to encode. If None, encodes all object/string columns
        that contain duplicate values.

    Returns
    -------
    pd.DataFrame
        DataFrame with selected columns converted to CategoricalDtype.
    """
    out = x.copy()
    if j is None:
        cols = [
            c
            for c in out.columns
            if (out[c].dtype == object or isinstance(out[c].dtype, pd.StringDtype))
            and out[c].duplicated().any()
        ]
    else:
        missing = [c for c in j if c not in out.columns]
        if missing:
            msg = f"Columns not found: {missing!r}"
            raise ValueError(msg)
        cols = j
    for col in cols:
        out[col] = out[col].astype("category")
    return out
