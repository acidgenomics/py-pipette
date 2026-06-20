"""Concatenate strings to form a URL."""


def paste_url(*args: str, protocol: str = "none") -> str:
    """Concatenate strings to form a URL path.

    Parameters
    ----------
    *args : str
        Path components to join.
    protocol : str
        Protocol prefix. One of ``"none"``, ``"https"``, ``"http"``,
        ``"ftp"``, ``"s3"``. Default is ``"none"`` (no prefix added).

    Returns
    -------
    str
        Concatenated URL with components joined by ``/``.
    """
    parts = [a.rstrip("/") for a in args]
    url = "/".join(parts)
    if protocol != "none":
        url = f"{protocol}://{url}"
    return url
