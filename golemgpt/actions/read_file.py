from pathlib import Path

MAX_SIZE = 2048


def read_file_action(filename: str, **kwargs) -> str:
    """Read a file and return its content."""
    cwd, path = Path.cwd(), Path(filename)
    try:
        path.relative_to(cwd)
    except ValueError:
        return "Rejected, file is outside of working dir."

    if not path.exists():
        return "Rejected, file does not exist."

    if path.stat().st_size > MAX_SIZE:
        return f"Rejected, file is large (max {MAX_SIZE})."

    with path.open("r") as file:
        return file.read()
