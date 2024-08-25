from secrets import token_hex
from time import time
from typing import Optional, Union
from golemgpt.utils.misc import workpath
from golemgpt.utils.http import http_download, RequestError

HTTP_REQUEST_PROMPT = """
Response saved to {out_filename} ({file_size} bytes).
""".strip()


def http_download_action(
    url: str, method: str = "GET", out_filename: str = "",
    headers: Optional[dict] = None,
    body: Union[str, list, dict] = None,
    **kwargs
) -> str:
    """Make HTTP request, save result to file (JSON, PNG, PDF, etc.)"""

    if not out_filename:
        out_filename = f"out_{int(time())}_{token_hex(12)}.txt"

    try:
        path = workpath(out_filename)
    except ValueError:
        return f"File {out_filename} is outside of working dir."

    try:
        response = http_download(
            method=method, url=url, path=path, headers=headers,
            json=body if isinstance(body, (dict, list)) else None,
            body=body if isinstance(body, str) else None,
        )
    except RequestError as error:
        return f"HTTP request failed: {error}"

    if response.status in (401, 403):
        return "HTTP request unauthorized: let's ask user for credentials?"

    file_size = path.stat().st_size
    return HTTP_REQUEST_PROMPT.format(
        out_filename=out_filename, file_size=file_size
    )
