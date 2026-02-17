"""Fetch JSON from a URL."""

import json
import urllib.request


def get_json(url: str) -> dict | list:
    """Fetch and parse JSON from a URL.

    Parameters
    ----------
    url : str
        URL to a JSON resource.

    Returns
    -------
    dict or list
        Parsed JSON data.
    """
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))
