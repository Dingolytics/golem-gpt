from json import dumps as json_dumps
from golemgpt.utils import workpath


def write_file_action(filename: str, content: str, **kwargs) -> str:
    """Write a file and return its info."""
    path = workpath(filename)

    if not isinstance(content, str):
        content = json_dumps(content)

    with path.open("w") as file:
        file.write(content)

    return f'File "{filename}" is saved.'
