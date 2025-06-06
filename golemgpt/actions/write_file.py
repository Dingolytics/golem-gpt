from json import dumps as json_dumps
from golemgpt.utils import workpath


def write_file_action(filename: str, content: str | dict, **kwargs) -> str:
    """Write a text file."""
    path = workpath(filename)

    if not isinstance(content, str):
        content = json_dumps(content)

    with path.open("w") as file:
        file.write(content)

    file_size = path.stat().st_size
    return f'File "{filename}" is saved ({file_size} bytes).'
