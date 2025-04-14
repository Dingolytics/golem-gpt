from typing import Any, Dict, Optional
from json import dumps as json_dumps, loads as json_loads
import urllib3
import urllib3.exceptions

http = urllib3.PoolManager()

BaseHTTPResponse = urllib3.BaseHTTPResponse

RequestError = urllib3.exceptions.RequestError

DEFAULT_TIMEOUT = 30.0


def _do_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None,
    **kwargs: Any,
) -> BaseHTTPResponse:
    """Send an HTTP request helper."""
    if json:
        headers = headers or {}
        headers.update(
            {
                "content-type": "application/json",
                # "user-agent": (
                #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                #     "AppleWebKit/537.36 (KHTML, like Gecko) "
                #     "Chrome/122.0.0.0 Safari/537.36"
                # ),
                # "DNT": "1",  # Do Not Track
            }
        )
        kwargs["body"] = json_dumps(json)
    return http.request(method=method, url=url, headers=headers, **kwargs)


def http_request_streamed(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None,
    **kwargs: Any,
) -> BaseHTTPResponse:
    """Send an HTTP request without preloading, i.e. streamed."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return _do_request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        preload_content=False,
        **kwargs,
    )


def http_download(
    method: str,
    url: str,
    path: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None,
    **kwargs: Any,
) -> BaseHTTPResponse:
    """Download file via streamed HTTP request."""
    response = http_request_streamed(
        method=method, url=url, headers=headers, json=json, **kwargs
    )
    with open(path, "wb") as file:
        for chunk in response.stream():
            file.write(chunk)
    return response


def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None,
    json_result: bool = False,
    **kwargs: Any,
) -> BaseHTTPResponse:
    """Send an HTTP request and return response."""
    response = _do_request(
        method=method, url=url, headers=headers, json=json, **kwargs
    )
    if response.status == 200:
        return response
    raise RuntimeError(f"HTTP request failed: {response.data}")


def http_request_as_json(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Send an HTTP request and return parsed data."""
    response = http_request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        json_result=True,
        **kwargs,
    )
    data = json_loads(response.data)
    assert isinstance(data, dict)
    return data
