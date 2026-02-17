"""File checksum functions."""

import hashlib


def md5(path: str) -> str:
    """Calculate MD5 checksum of a file.

    Parameters
    ----------
    path : str
        Path to the file.

    Returns
    -------
    str
        Hexadecimal MD5 digest.
    """
    return _hash_file(path, "md5")


def sha256(path: str) -> str:
    """Calculate SHA-256 checksum of a file.

    Parameters
    ----------
    path : str
        Path to the file.

    Returns
    -------
    str
        Hexadecimal SHA-256 digest.
    """
    return _hash_file(path, "sha256")


def _hash_file(path: str, algo: str) -> str:
    """Hash a file with the specified algorithm."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
