"""Match row name column in a DataFrame."""

import pandas as pd

_ROWNAME_PATTERNS = {"rn", "row.name", "row.names", "rowname", "rownames"}


def match_rowname_column(df: pd.DataFrame) -> str | None:
    """Detect a row name column in a DataFrame.

    Checks for columns matching common row name patterns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    str or None
        Name of the detected row-name column, or ``None`` if no column
        matches a known pattern with unique values.
    """
    if not isinstance(df, pd.DataFrame):
        return None
    for col in df.columns:
        if col.lower() in _ROWNAME_PATTERNS and df[col].is_unique:
            return col
    return None
