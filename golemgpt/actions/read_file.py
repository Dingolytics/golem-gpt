from golemgpt.utils import workpath
from .summarize_file import summarize_file_action

MAX_RAW_SIZE = 8096


def read_file_action(filename: str, **kwargs) -> str:
    """Read a file and return its content."""
    path = workpath(filename, check_exists=True)
    file_size = path.stat().st_size
    if file_size > MAX_RAW_SIZE:
        hint = kwargs.get('summazie_hint') or "essential data is needed"
        return summarize_file_action(
            filename, hint=hint, **kwargs
        )
        # raise PathRejected(
        #     f"Error, file '{filename}' is too large ({file_size} bytes)."
        # )
    with path.open("r") as file:
        return file.read()
