from typing import Any, Tuple

from golemgpt.runners.base import BaseRunner
from golemgpt.types import ActionItem
from golemgpt.utils.exceptions import UnknownAction


class JustDoRunner(BaseRunner):
    """A naive runner that just performs the specified action."""

    def __call__(self, action_item: ActionItem, golem: Any) -> Tuple[str, str]:
        for key in action_item:
            if key not in self.known_actions:
                raise UnknownAction(str(action_item))
            action_fn = self.known_actions[key]
            kwargs = action_item[key]
            result = action_fn(golem=golem, **kwargs)
            return (key, result)
        raise UnknownAction(str(action_item))
