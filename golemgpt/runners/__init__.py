from typing import Callable
from golemgpt.settings import Settings
from .justdo import JustDoRunner

__all__ = [
    'JustDoRunner',
]


def default_runner(settings: Settings) -> Callable:
    return JustDoRunner(settings)
