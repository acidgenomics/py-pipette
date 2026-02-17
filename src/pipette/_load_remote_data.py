"""Load data from a remote URL."""

from pipette._cache_url import cache_url
from pipette._import import import_data


def load_remote_data(
    url: str,
    quiet: bool = False,
) -> object:
    """Download and import data from a remote URL.

    The file is cached locally for subsequent calls.

    Parameters
    ----------
    url : str
        URL to a remote data file.
    quiet : bool
        Suppress messages.

    Returns
    -------
    object
        Imported data.
    """
    path = cache_url(url)
    if not quiet:
        print(f"Loading from cache: {path}")
    return import_data(path, quiet=quiet)
