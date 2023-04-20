from termcolor import cprint, colored


def message(author: str, text: str, color='white') -> None:
    author = colored(author.upper(), 'magenta')
    cprint(author + '\n' + text + '\n', color)


def info(text: str) -> None:
    cprint(text, 'cyan')


def debug(text: str, indent='    ') -> None:
    indented = '\n'.join([f'{indent}{x}' for x in text.splitlines()])
    cprint(indented, 'dark_grey')
