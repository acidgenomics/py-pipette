"""Load serialized data from local files."""

import glob
import os

from pipette._import import import_data


def load_data(
    *names: str,
    dir: str = ".",
    quiet: bool = False,
) -> object:
    """Load data by name from a directory.

    Searches for files matching the given name(s) with any supported
    extension.

    Parameters
    ----------
    *names : str
        Object names to load (without extension).
    dir : str
        Directory to search.
    quiet : bool
        Suppress messages.

    Returns
    -------
    object
        Loaded data. If multiple names given, returns a dict.
    """
    results = {}
    for name in names:
        pattern = os.path.join(dir, name + ".*")
        matches = glob.glob(pattern)
        if not matches:
            raise FileNotFoundError(f"No file found for {name!r} in {dir!r}.")
        path = matches[0]
        if not quiet:
            print(f"Loading {path}")
        results[name] = import_data(path, quiet=quiet)
    if len(names) == 1:
        return results[names[0]]
    return results
