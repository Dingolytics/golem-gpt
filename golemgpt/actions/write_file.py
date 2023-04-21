from json import dumps as json_dumps
from pathlib import Path

MAX_SIZE = 2048


def write_file_action(filename: str, content: str, **kwargs) -> str:
    """Write a file and return its info."""
    cwd, path = Path.cwd(), (Path.cwd() / filename)
    try:
        path.relative_to(cwd)
    except ValueError:
        return "Rejected, file is outside of working dir."

    if not isinstance(content, str):
        content = json_dumps(content)

    with path.open("w") as file:
        file.write(content)

    return f"File {path} is saved."
