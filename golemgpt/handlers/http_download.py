from mimetypes import guess_extension
from pathlib import Path
from secrets import token_hex
from time import time
from typing import Any

from pydantic import field_validator

from golemgpt.handlers.base import BaseHandler, BaseOutput, BaseParams
from golemgpt.utils.misc import workpath
from golemgpt.utils.exceptions import PathRejected, WorkflowError
from golemgpt.utils.http import (
    BaseHTTPResponse,
    RequestError,
    http_download,
    http_request,
)

# Mapping to use "canonical" file extensions for output.
EXT_ALIASES = {
    ".jpeg": ".jpg",
}


class RequestTypeError(WorkflowError):
    pass


class HttpDownloadParams(BaseParams):
    url: str
    method: str = "GET"
    out_filename: str = ""
    headers: dict[str, str] = {}
    body: str | bytes | list | dict | None = None

    @field_validator("out_filename", mode="after")
    @classmethod
    def set_out_filename(cls, value: str) -> str:
        if not value.strip():
            return f"out_{int(time())}_{token_hex(12)}.txt"
        for alias in EXT_ALIASES:
            if value.lower().endswith(alias):
                value = value[-len(alias):] + EXT_ALIASES[alias]
        return value


class HttpDownloadHandler(BaseHandler[HttpDownloadParams]):
    params_cls = HttpDownloadParams

    description = "Make HTTP request, save result to file (JSON, PNG, etc.)"

    success_prompt = "Response saved to {out_filename} ({file_size} bytes)."

    wrong_link_error = (
        "Error trying to download '{output_ext}' file "
        "from '{content_ext}' URL. Download file as {guess_ext} first "
        "and then extract links using the provided summary tool."
    )

    image_mismatch_error = (
        "Error trying to download '{output_ext}' file "
        "from '{content_ext}' URL."
    )

    text_formats = (".html", ".txt")

    image_formats = (".svg", ".png", ".jpg", ".heic", ".webp")

    def validate_params(self, params: dict[str, Any]) -> HttpDownloadParams:
        validated = super().validate_params(params)

        head_response = http_request(method="HEAD", url=validated.url)

        content_type = head_response.headers.get("content-type") or ""
        content_type = content_type.split(" ")[0]
        content_type = content_type.rstrip(";")

        output_ext = Path(validated.out_filename).suffix.lower()
        content_ext = guess_extension(content_type)

        # TODO: More robust content types matching.
        if content_ext in self.text_formats:
            if output_ext not in self.text_formats:
                error = self.wrong_link_error.format(
                    content_ext=content_ext,
                    output_ext=output_ext,
                )
                raise RequestTypeError(error)

        if content_ext in self.image_formats:
            if output_ext != content_ext:
                error = self.image_mismatch_error.format(
                    content_ext=content_ext,
                    output_ext=output_ext,
                )
                raise RequestTypeError(error)

        return validated

    def do_action(self, params: HttpDownloadParams | None) -> BaseOutput:
        assert params

        try:
            path, response = self._do_download(params)
        except PathRejected as exc:
            return BaseOutput(error_feedback=str(exc))
        except RequestError as exc:
            return BaseOutput(error_feedback=f"HTTP request failed: {exc}")

        if response.status in (401, 403):
            return BaseOutput(error_feedback="HTTP request unauthorized")

        result = self.success_prompt.format(
            out_filename=params.out_filename,
            file_size=path.stat().st_size,
        )

        return BaseOutput(result=result)

    def _do_download(
        self, params: HttpDownloadParams
    ) -> tuple[Path, BaseHTTPResponse]:
        path = workpath(params.out_filename)
        method = params.method
        url = params.url
        headers = params.headers
        body = params.body

        response = http_download(
            method=method,
            url=url,
            path=str(path),
            headers=headers,
            json=body if isinstance(body, (dict, list)) else None,
            body=body if isinstance(body, str) else None,
        )

        return path, response
