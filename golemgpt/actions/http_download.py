from typing import Optional, Union
from golemgpt.utils.misc import workpath
from golemgpt.utils.http import http_download

HTTP_REQUEST_PROMPT = """
Response saved to {out_filename} ({file_size} bytes).
""".strip()


def http_download_action(
    url: str, method: str, out_filename: str,
    headers: Optional[dict] = None,
    body: Union[str, list, dict] = None,
    **kwargs
) -> str:
    """Make an HTTP request and return its content."""
    try:
        path = workpath(out_filename)
    except ValueError:
        return f"File {out_filename} is outside of working dir."

    response = http_download(
        method=method, url=url, path=path, headers=headers,
        json=body if isinstance(body, (dict, list)) else None,
        body=body if isinstance(body, str) else None,
    )

    if response.status in (401, 403):
        return "HTTP request failed: maybe ask user for credentials?"

    file_size = path.stat().st_size
    return HTTP_REQUEST_PROMPT.format(
        out_filename=out_filename, file_size=file_size
    )
