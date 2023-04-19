from typing import Tuple
from gptgolem.settings import Settings
from gptgolem.actions import ALL_KNOWN_ACTIONS


class JustDoRunner:
    """A naive runner that just performs the specified action."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.known_actions = ALL_KNOWN_ACTIONS

    def __call__(self, action: dict) -> Tuple[str, str]:
        for key in action:
            if key not in self.known_actions:
                print(f"Unknown action: {key}")
                return key, ''
            action_fn = self.known_actions[key]
            kwargs = action[key]
            result = action_fn(**kwargs)
            break
        return (key, result)
