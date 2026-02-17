"""Get and set metadata on DataFrames."""

from typing import Any

import pandas as pd


def metadata2(df: pd.DataFrame, key: str, set_value: Any = None) -> Any:
    """Get or set metadata on a DataFrame using attrs.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    key : str
        Metadata key.
    set_value : optional
        If provided, sets the metadata value.

    Returns
    -------
    The metadata value when getting, or None when setting.
    """
    if set_value is not None:
        df.attrs[key] = set_value
        return None
    return df.attrs.get(key, None)
