import time
import random
import string


def genkey() -> str:
    prefix = hex(int(time.time()))[1:]
    suffix = ''.join(random.choices(string.ascii_lowercase, k=3))
    return f'{prefix}-{suffix}'
