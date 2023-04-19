from typing import Any, Dict, Optional, Union
from json import dumps as json_dumps, loads as json_loads
import urllib3

http = urllib3.PoolManager()


def http_request(
        method: str, url: str, headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None, **kwargs: Any
    ) -> Union[Dict[str, Any], bytes]:
    """Send an HTTP request."""
    if json:
        headers = headers or {}
        headers['content-type'] = 'application/json'
        body = json_dumps(json)
    else:
        body = None
    response = http.request(
        method=method, url=url, headers=headers, body=body, **kwargs
    )
    if response.status == 200:
        if response.headers['content-type'] == 'application/json':
            return json_loads(response.data)
        return response.data
    raise RuntimeError(f'HTTP request failed: {response}')
