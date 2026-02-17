"""Save data to files."""

import os
from typing import Any

from pipette._export import export_data


def save_data(
    x: Any,
    name: str,
    dir: str = ".",
    ext: str = "csv",
    overwrite: bool = True,
    quiet: bool = False,
) -> str:
    """Save data to a file.

    Parameters
    ----------
    x : object
        Data to save.
    name : str
        Object name (used as filename stem).
    dir : str
        Output directory.
    ext : str
        File extension/format.
    overwrite : bool
        Overwrite existing files.
    quiet : bool
        Suppress messages.

    Returns
    -------
    str
        Path to the saved file.
    """
    os.makedirs(dir, exist_ok=True)
    path = os.path.join(dir, f"{name}.{ext}")
    return export_data(x, path, overwrite=overwrite, quiet=quiet)
