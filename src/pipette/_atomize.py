"""Atomize a DataFrame by keeping only scalar columns."""

import pandas as pd


def atomize(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only columns containing scalar (atomic) values.

    Removes columns where any value is a list, dict, set, or other
    non-scalar type.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with only scalar columns.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a DataFrame.")
    keep = []
    for col in df.columns:
        is_scalar = True
        for val in df[col]:
            if isinstance(val, (list, dict, set, tuple)):
                is_scalar = False
                break
        if is_scalar:
            keep.append(col)
    return df[keep].copy()
