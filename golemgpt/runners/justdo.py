from typing import Any, Optional, Tuple
from golemgpt.settings import Settings
from golemgpt.utils.exceptions import UnknownAction
from golemgpt.actions import ALL_KNOWN_ACTIONS


class JustDoRunner:
    """A naive runner that just performs the specified action."""

    def __init__(
        self, settings: Settings, known_actions: Optional[dict] = None
    ) -> None:
        self.settings = settings
        self.known_actions = known_actions or ALL_KNOWN_ACTIONS

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __call__(self, action_item: dict, golem: Any) -> Tuple[str, str]:
        for key in action_item:
            if key not in self.known_actions:
                raise UnknownAction(key)
            action_fn = self.known_actions[key]
            kwargs = action_item[key]
            result = action_fn(golem=golem, **kwargs)
            break
        return (key, result)
