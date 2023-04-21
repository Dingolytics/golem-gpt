import time
import random
import string
from pathlib import Path


def genkey() -> str:
    prefix = hex(int(time.time()))[1:]
    suffix = ''.join(random.choices(string.ascii_lowercase, k=3))
    return f'{prefix}-{suffix}'


def workpath(relpath: str) -> Path:
    cwd = Path.cwd().absolute()
    path = Path(Path.cwd() / relpath).absolute()
    if cwd in path.parents:
        return path
    raise ValueError(f"File {relpath} is outside of working dir.")
