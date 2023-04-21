from json import dumps as json_dumps
from pathlib import Path

MAX_SIZE = 2048


def write_file_action(filename: str, content: str, **kwargs) -> str:
    """Write a file and return its info."""
    cwd = Path.cwd().absolute()
    path = Path(Path.cwd() / filename).absolute()

    if cwd in path.parents:
        relname = path.relative_to(cwd)
    else:
        return f"Rejected, file {filename} is outside of working dir."

    if not isinstance(content, str):
        content = json_dumps(content)

    with path.open("w") as file:
        file.write(content)

    return f'File "{relname}" is saved.'
