from typing import Any

from bs4 import BeautifulSoup, PageElement
from pydantic import BaseModel

from golemgpt.handlers.base import BaseHandler, BaseOutput, BaseParams
from golemgpt.utils.misc import workpath


class ImageLink(BaseModel):
    url: str
    hint: str = ""


def extract_images_from_html(content: str) -> list[ImageLink]:
    soup = BeautifulSoup(content, "html.parser")
    images = []

    img_tags: list[PageElement] = soup.find_all("img")
    for tag in img_tags:
        url = tag.get("src")
        alt_text = tag.get("alt", "")
        title = tag.get("title", "")

        # Use alt text first, fallback to title if alt is empty
        hint = alt_text if alt_text else title

        if url:
            images.append(ImageLink(url=url, hint=hint))

    return images


class ExtractImagesParams(BaseParams):
    filename: str


class ExtractImagesHandler(BaseHandler):
    params_cls = ExtractImagesParams

    description = "Extract images links from HTML file."

    def validate_params(self, params: dict[str, Any]) -> ExtractImagesParams:
        validated = super().validate_params(params)

        path = workpath(validated.filename)
        if not path.exists():
            raise Exception("File is missing, please download file first.")

        return validated

    def do_action(self, params: ExtractImagesParams | None) -> BaseOutput:
        assert params

        path = workpath(params.filename)
        content = path.read_text()
        images = extract_images_from_html(content)

        links_formatted: list[str] = []

        for img in images:
            image_hint = img.hint or "(no image hint)"
            image_text = f"{image_hint}:\n{img.url}"
            links_formatted.append(image_text)

        return BaseOutput(result="\n\n".join(links_formatted))
