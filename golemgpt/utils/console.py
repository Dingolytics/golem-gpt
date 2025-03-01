from termcolor import cprint, colored
from termcolor._types import Color

_DEBUG = False

_COLORS: list[Color] = ["light_red", "green", "yellow", "blue", "light_magenta"]


def set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled


def get_indent(tags: list[str] | None = None) -> int:
    """Get indentation for output based on tags."""
    if tags:
        if "reply" in tags:
            return 4
    return 0


def message(author: str, text: str, tags: list[str] | None = None) -> None:
    indent = get_indent(tags)
    author = author.upper()
    idx = sum(ord(char) for char in author) % len(_COLORS)
    author_color = _COLORS[idx]
    title = author + (f" [{', '.join(tags)}]" if tags else "")
    title = " " * indent + title
    text = "\n".join([" " * indent + line for line in text.split("\n")])
    cprint(colored(title, author_color, None, []))
    print(text)
    print("")


def info(text: str) -> None:
    cprint(text, "cyan")


def debug(text: str, indent="    ") -> None:
    if _DEBUG:
        indented = "\n".join([f"{indent}{x}" for x in text.splitlines()])
        cprint(indented, "grey")
