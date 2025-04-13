from typing import Tuple

from golemgpt.handlers.base import BaseHandler
from golemgpt.runners.base import BaseRunner
from golemgpt.types import ActionItem
from golemgpt.utils.exceptions import UnknownAction


class JustDoRunner(BaseRunner):
    """A naive runner that just performs the specified action."""

    def __call__(self, action_item: ActionItem) -> Tuple[str, str]:
        key, params = next(iter(action_item.items()))

        if key not in self.known_actions:
            raise UnknownAction(str(action_item))

        action_fn = self.known_actions[key]

        if isinstance(action_fn, type):
            assert issubclass(action_fn, BaseHandler)
            handler = action_fn()
            output = handler(params)
            result = output.result
        else:
            result = action_fn(golem=self.golem, **params)

        return (key, result)
