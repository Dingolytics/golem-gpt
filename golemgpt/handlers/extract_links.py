from typing import Any

from bs4 import BeautifulSoup, PageElement
from pydantic import BaseModel

from golemgpt.handlers.base import BaseHandler, BaseOutput, BaseParams
from golemgpt.utils.misc import workpath


class ClickableLink(BaseModel):
    url: str
    clickable: str = ""
    hint: str = ""


def extract_links_from_html(content: str) -> list[ClickableLink]:
    soup = BeautifulSoup(content, "html.parser")
    links = []

    a_tags: list[PageElement] = soup.find_all("a", href=True)
    for tag in a_tags:
        url = tag.get("href")
        hint = tag.get("title", "")
        clickable = tag.get_text(strip=True) or ""

        if url:
            links.append(ClickableLink(url=url, clickable=clickable, hint=hint))

    return links


class ExtractLinksParams(BaseParams):
    filename: str


class ExtractLinksHandler(BaseHandler):
    params_cls = ExtractLinksParams

    description = "Extract clickable links from HTML file."

    def validate_params(self, params: dict[str, Any]) -> ExtractLinksParams:
        validated = super().validate_params(params)

        path = workpath(validated.filename)
        if not path.exists():
            raise Exception("File is missing, please download file first.")

        return validated

    def do_action(self, params: ExtractLinksParams | None) -> BaseOutput:
        assert params

        path = workpath(params.filename)
        content = path.read_text()
        links = extract_links_from_html(content)

        links_formatted: list[str] = []

        for link in links:
            clickable_text = link.clickable or "(no clickable text)"
            link_text = f"{clickable_text}:\n{link.url}"
            if link.hint:
                link_text += f"\n({link.hint})"
            links_formatted.append(link_text)

        return BaseOutput(result="\n\n".join(links_formatted))
