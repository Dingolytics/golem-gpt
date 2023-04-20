from typing import Any, Tuple
from gptgolem.settings import Settings
from gptgolem.actions import ALL_KNOWN_ACTIONS, UnknownAction


class JustDoRunner:
    """A naive runner that just performs the specified action."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.known_actions = ALL_KNOWN_ACTIONS

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __call__(self, action_item: dict, golem: Any) -> Tuple[str, str]:
        for key in action_item:
            if key not in self.known_actions:
                raise UnknownAction(key)
            action_fn = self.known_actions[key]
            kwargs = action_item[key]
            result = action_fn(**kwargs)
            break
        return (key, result)
