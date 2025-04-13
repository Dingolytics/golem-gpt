# from typing import override

from golemgpt.handlers.base import BaseHandler, BaseOutput, BaseParams


class HttpDownloadParams(BaseParams):
    url: str
    method: str = "GET"
    out_filename: str = ""
    headers: dict = {}
    body: str | bytes | list | dict | None = None


class HttpDownloadHandler(BaseHandler[HttpDownloadParams]):
    params_cls = HttpDownloadParams

    description = """
        Make HTTP request, save result to file (JSON, PNG, PDF, etc.)
    """.strip()

    def do_action(self, params: HttpDownloadParams | None) -> BaseOutput:
        return BaseOutput(result="")
