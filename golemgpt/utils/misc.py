
import time
import random
import string
from pathlib import Path
from .exceptions import PathRejected


def genkey() -> str:
    prefix = hex(int(time.time()))[1:]
    suffix = ''.join(random.choices(string.ascii_lowercase, k=3))
    return f'{prefix}-{suffix}'


def workpath(relpath: str, check_exists: bool = False) -> Path:
    cwd = Path.cwd().absolute()
    path = Path(Path.cwd() / relpath).absolute()
    if cwd not in path.parents:
        raise PathRejected(
            relpath, f"File {relpath} is outside of working dir."
        )
    if check_exists and not path.exists():
        raise PathRejected(
            relpath, f"File {relpath} does not exist."
        )
    return path
