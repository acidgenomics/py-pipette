"""Cache remote files locally."""

import hashlib
import os
import urllib.request

from pipette._file_utils import basename_sans_ext, file_ext


def cache_url(
    url: str,
    pkg: str = "pipette",
    update: bool = False,
) -> str:
    """Download and cache a URL locally.

    Files are cached in ``~/.cache/<pkg>/``.

    Parameters
    ----------
    url : str
        URL to download.
    pkg : str
        Package name for cache subdirectory.
    update : bool
        Force re-download if True.

    Returns
    -------
    str
        Path to the cached file.
    """
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", pkg)
    os.makedirs(cache_dir, exist_ok=True)
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    # Strip query string and fragment before extracting filename parts,
    # otherwise ext/name will include '?token=abc' etc.
    url_path = url.split("?", 1)[0].split("#", 1)[0]
    ext = file_ext(url_path)
    name = basename_sans_ext(url_path)
    filename = f"{name}_{url_hash}"
    if ext:
        filename += "." + ext
    dest = os.path.join(cache_dir, filename)
    if os.path.isfile(dest) and not update:
        return dest
    urllib.request.urlretrieve(url, dest)
    return dest
