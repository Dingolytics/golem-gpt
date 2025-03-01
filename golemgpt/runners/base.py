from typing import Any, Tuple
from golemgpt.types import ActionItem


class BaseRunner:
    """Base action runner class."""

    def __init__(self, golem: Any) -> None:
        from golemgpt.golems.general import GeneralGolem  # avoid circular

        assert isinstance(golem, GeneralGolem)

        self.golem = golem
        self.settings = self.golem.settings
        self.known_actions = self.golem.actions

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __call__(self, action_item: ActionItem) -> Tuple[str, str]:
        raise NotImplementedError()
