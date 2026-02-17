"""Get directory listing from a URL."""

import re
import urllib.request
from ftplib import FTP
from urllib.parse import ParseResult, urlparse


def get_url_dir_list(url: str) -> list[str]:
    """Get a directory listing from an FTP or HTTP URL.

    Parameters
    ----------
    url : str
        URL to a directory.

    Returns
    -------
    list of str
        File and directory names.
    """
    parsed = urlparse(url)
    if parsed.scheme == "ftp":
        return _ftp_dir_list(parsed)
    return _http_dir_list(url)


def _ftp_dir_list(parsed: ParseResult) -> list[str]:
    """Get FTP directory listing."""
    ftp = FTP(parsed.hostname)
    ftp.login()
    entries = ftp.nlst(parsed.path)
    ftp.quit()
    return [e.rsplit("/", 1)[-1] for e in entries]


def _http_dir_list(url: str) -> list[str]:
    """Parse directory listing from HTTP index page."""
    with urllib.request.urlopen(url) as resp:
        html = resp.read().decode("utf-8")
    links = re.findall(r'href="([^"]+)"', html)
    entries = []
    for link in links:
        if link.startswith("?") or link.startswith("/"):
            continue
        entries.append(link.rstrip("/"))
    return entries
