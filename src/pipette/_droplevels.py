"""Remove unused categories from Categorical columns."""

import pandas as pd


def droplevels(x: pd.DataFrame, *, j: list[str] | None = None) -> pd.DataFrame:
    """Remove unused categories from Categorical columns.

    Parameters
    ----------
    x : pd.DataFrame
        Input DataFrame.
    j : list of str, optional
        Column names to process. If None, applies to all Categorical columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with unused categories removed.
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
        out[col] = out[col].cat.remove_unused_categories()
    return out
