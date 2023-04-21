from typing import Optional, Union
from golemgpt.utils.misc import workpath
from golemgpt.utils.http import http_request_streamed

HTTP_REQUEST_PROMPT = """
Response saved to {out_filename} ({file_size} bytes).
""".strip()


def http_request_action(
    url: str, method: str, out_filename: str,
    headers: Optional[dict] = None,
    body: Union[str, list, dict] = None,
    **kwargs
) -> str:
    """Make an HTTP request and return its content."""
    path = workpath(out_filename)
    response = http_request_streamed(
        method=method, url=url, headers=headers,
        json=body if isinstance(body, (dict, list)) else None,
        body=body if isinstance(body, str) else None,
    )
    with path.open('wb') as file:
        for chunk in response.stream():
            file.write(chunk)
    file_size = path.stat().st_size
    return HTTP_REQUEST_PROMPT.format(
        out_filename=out_filename, file_size=file_size
    )
