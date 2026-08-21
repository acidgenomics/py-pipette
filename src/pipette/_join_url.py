"""Join strings to form a URL."""


def join_url(*args: str, protocol: str | None = None) -> str:
    """Join strings to form a URL path.

    Parameters
    ----------
    *args : str
        Path components to join.
    protocol : str, optional
        Protocol prefix. One of ``"https"``, ``"http"``, ``"ftp"``,
        ``"s3"``. Default is ``None`` (no prefix added).

    Returns
    -------
    str
        Joined URL with components joined by ``/``.
    """
    parts = [a.rstrip("/") for a in args]
    url = "/".join(parts)
    if protocol is not None:
        url = f"{protocol}://{url}"
    return url
