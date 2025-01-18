from time import time
from pathlib import Path

from bs4 import BeautifulSoup
from golemgpt.utils import console, workpath
from .write_file import write_file_action

MAX_RAW_SIZE = 65536 * 2  # 65K tokens for GPT-4o-mini


def distill_html_file(path: Path, indent: int = 0) -> str:
    console.info(f"Distilling HTML file: {path}")
    soup = BeautifulSoup(path.read_text(), "html.parser")
    if indent == 0:
        return soup.get_text(separator="\n", strip=True)
    else:
        # Build indented text representation preserving hierarchy
        text = []
        ref_depth = 0
        current_depth = 0
        # base_depth = 0
        for tag in soup.find_all(True):
            # Skip style tags and their content
            if tag.name in {"style", "script"}:
                continue
            # Skip empty, whitespace-only, or CSS/special content tags
            content = tag.string
            if not content or not content.strip():
                continue
            # Skip if this text is also in a child tag
            if any(ch for ch in tag.find_all() if ch.string == content):
                continue
            # Calculate indent level based on parent tags
            depth = 0
            parent = tag.parent
            while parent and parent.name != "[document]":
                depth += 1
                parent = parent.parent
            if depth > ref_depth:
                current_depth += 1
            elif depth < ref_depth:
                current_depth -= 1
            ref_depth = depth
            # Add indented text
            text.append(' ' * (current_depth * indent) + content.strip())
        return '\n'.join(text)


def distill_file_known_formats(path: Path) -> str | None:
    if path.suffix == ".html":
        return distill_html_file(path, indent=2)

    return None


def summarize_file_action(
    filename: str, hint: str, **kwargs
) -> str:
    # TODO: Better way to import for type checking
    from golemgpt.golems import GeneralGolem  # noqa
    golem = kwargs['golem']  # type: GeneralGolem
    # TODO: Split file into chunks for summarization
    path = workpath(filename, check_exists=True)

    content = distill_file_known_formats(path)
    if content is None:
        with path.open("r") as file:
            content = file.read()
        content = content[:MAX_RAW_SIZE]

    cognitron = golem.cognitron(name="Summarizer")
    prompt = f"{hint.rstrip('.')}. From the following text:\n\n{content}"
    reply = cognitron.communicate(prompt)
    reply_text = reply.text
    out_filename = f"summarized_{int(time())}_{filename}.txt"

    return write_file_action(out_filename, reply_text)
