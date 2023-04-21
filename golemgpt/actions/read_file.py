from pathlib import Path

MAX_SIZE = 8096


def read_file_action(filename: str, **kwargs) -> str:
    """Read a file and return its content."""
    cwd = Path.cwd().absolute()
    path = Path(Path.cwd() / filename).absolute()

    if cwd in path.parents:
        relname = path.relative_to(cwd)
    else:
        return f"Rejected, file {filename} is outside of working dir."

    if not path.exists():
        return f"Rejected, file {relname} does not exist."

    file_size = path.stat().st_size
    if path.stat().st_size > MAX_SIZE:
        return f"File exists, but is too large ({file_size} bytes)."

    with path.open("r") as file:
        return file.read()
