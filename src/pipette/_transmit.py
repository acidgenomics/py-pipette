"""Transmit (download) files from FTP/HTTP."""

import fnmatch
import os
import urllib.request
from urllib.parse import urljoin

from pipette._get_url_dir_list import get_url_dir_list


def transmit(
    url: str,
    dir: str = ".",
    pattern: str | None = None,
    quiet: bool = False,
) -> list[str]:
    """Download files from a remote directory.

    Parameters
    ----------
    url : str
        URL to a remote directory.
    dir : str
        Local directory to save files.
    pattern : str, optional
        Glob pattern to filter files.
    quiet : bool
        Suppress messages.

    Returns
    -------
    list of str
        Paths to downloaded files.
    """
    os.makedirs(dir, exist_ok=True)
    entries = get_url_dir_list(url)
    if pattern is not None:
        entries = [e for e in entries if fnmatch.fnmatch(e, pattern)]
    paths = []
    for entry in entries:
        file_url = urljoin(url.rstrip("/") + "/", entry)
        dest = os.path.join(dir, entry)
        if not quiet:
            print(f"Downloading {file_url} -> {dest}")
        urllib.request.urlretrieve(file_url, dest)
        paths.append(dest)
    return paths
