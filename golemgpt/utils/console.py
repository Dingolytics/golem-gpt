from termcolor import cprint, colored

_DEBUG = False

_COLORS = ['light_red', 'green', 'yellow', 'blue', 'light_magenta']


def set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled


def message(author: str, text: str) -> None:
    author = author.upper()
    idx = sum(ord(char) for char in author) % len(_COLORS)
    author_color = _COLORS[idx]
    cprint(colored(author, author_color, None, []))
    print(text)
    print('')


def info(text: str) -> None:
    cprint(text, 'cyan')


def debug(text: str, indent='    ') -> None:
    if _DEBUG:
        indented = '\n'.join([f'{indent}{x}' for x in text.splitlines()])
        cprint(indented, 'grey')
