from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import requests


def build_url(base_url: str, *path_parts: str) -> str:
    """
    Join a base URL and path components without introducing duplicate slashes.
    """
    return "/".join(
        [
            base_url.rstrip("/"),
            *(part.strip("/") for part in path_parts if part),
        ]
    )


def prepare_url(
    url: str,
    params: Mapping[str, str] | None = None,
) -> str:
    """
    Return the final URL that Requests will send, including encoded parameters.
    """
    request = requests.Request(
        method="GET",
        url=url,
        params=params,
    ).prepare()

    if request.url is None:
        raise ValueError(f"Failed to prepare request URL from {url!r}")

    return request.url


def print_request(method: str, url: str) -> None:
    """
    Print the request without printing headers, credentials, or request data.
    """
    print(f"{method.upper()} {url}")


def send_request(
    method: str,
    url: str,
    *,
    timeout: float,
    session: requests.Session | None = None,
    **kwargs: Any,
) -> requests.Response:
    """
    Print and send an HTTP request, raising for non-successful status codes.

    A session can be supplied for authenticated or persistent requests.
    Otherwise, the standard requests API is used.
    """
    print_request(method, url)

    request = requests.request if session is None else session.request

    response = request(
        method=method,
        url=url,
        timeout=timeout,
        **kwargs,
    )
    response.raise_for_status()

    return response
