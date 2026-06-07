"""Decode Categorical columns back to their base dtype."""

import pandas as pd


def decode(x: pd.DataFrame, *, j: list[str] | None = None) -> pd.DataFrame:
    """Decode Categorical columns back to their underlying type.

    Parameters
    ----------
    x : pd.DataFrame
        Input DataFrame.
    j : list of str, optional
        Column names to decode. If None, decodes all Categorical columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with Categorical columns converted back to base dtype.
    """
    out = x.copy()
    if j is None:
        cols = [c for c in out.columns if isinstance(out[c].dtype, pd.CategoricalDtype)]
    else:
        missing = [c for c in j if c not in out.columns]
        if missing:
            msg = f"Columns not found: {missing!r}"
            raise ValueError(msg)
        cols = [c for c in j if isinstance(out[c].dtype, pd.CategoricalDtype)]
    for col in cols:
        out[col] = out[col].astype(out[col].cat.categories.dtype)
    return out
