from typing import Any, Dict, Optional, Union
from json import dumps as json_dumps, loads as json_loads
import urllib3

http = urllib3.PoolManager()


def _do_request(
    method: str, url: str, headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None, **kwargs: Any
) -> urllib3.HTTPResponse:
    """Send an HTTP request helper."""
    if json:
        headers = headers or {}
        headers['content-type'] = 'application/json'
        kwargs['body'] = json_dumps(json)
    return http.request(
        method=method, url=url, headers=headers, **kwargs
    )


def http_request_streamed(
    method: str, url: str, headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None, **kwargs: Any
) -> urllib3.HTTPResponse:
    """Send an HTTP request without preloading, i.e. streamed."""
    return _do_request(
        method=method, url=url, headers=headers, json=json,
        preload_content=False, **kwargs
    )


def http_download(
    method: str, url: str, path: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None, **kwargs: Any
) -> urllib3.HTTPResponse:
    """Download file via streamed HTTP request."""
    response = http_request_streamed(
        method=method, url=url, headers=headers, json=json, **kwargs
    )
    with open(path, 'wb') as file:
        for chunk in response.stream():
            file.write(chunk)
    return response


def http_request(
    method: str, url: str, headers: Optional[Dict[str, str]] = None,
    json: Optional[Any] = None, json_result: bool = False, **kwargs: Any
) -> Union[Dict[str, Any], bytes]:
    """Send an HTTP request and return parsed data."""
    response = _do_request(
        method=method, url=url, headers=headers, json=json, **kwargs
    )
    content_type = response.headers["content-type"]
    # TODO: Guess more types if required (e.g. XML, CSV, query string)
    json_result = json_result or content_type in ("application/json",)
    if response.status == 200:
        if json_result:
            return json_loads(response.data)
        return response.data
    raise RuntimeError(f"HTTP request failed: {response.data}")
