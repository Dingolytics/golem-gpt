from typing import Any, Tuple

from golemgpt.runners.justdo import JustDoRunner
from golemgpt.types import ActionItem


class AlwaysAskRunner(JustDoRunner):
    """A runner that asks for confirmation before running an action."""

    def __call__(self, action_item: ActionItem, golem: Any) -> Tuple[str, str]:
        yes = input(f"Press Y to run action: {action_item}")
        if yes.lower() != "y":
            return "", ""
        return super().__call__(action_item, golem)
