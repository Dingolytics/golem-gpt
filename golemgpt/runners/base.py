from golemgpt.settings import Settings
from golemgpt.types import ActionFn


class BaseRunner:
    """Base action runner class."""

    def __init__(
        self, settings: Settings, known_actions: dict[str, ActionFn]
    ) -> None:
        self.settings = settings
        self.known_actions = known_actions

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"
