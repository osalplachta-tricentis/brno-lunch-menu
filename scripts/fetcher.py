"""HTTP fetching with a browser-like User-Agent.

Several of the target sites return ``403 Forbidden`` to the default
``python-requests`` User-Agent, so we always present a real browser UA.
"""

from __future__ import annotations

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT = 30


def fetch(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Return the decoded body of ``url`` or raise ``requests.HTTPError``."""
    resp = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "cs,en;q=0.8",
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    # Let requests pick the encoding from headers; fall back to the apparent
    # (chardet-detected) encoding when the server is vague, so Czech diacritics
    # survive.
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding
    return resp.text
