from gptgolem.settings import Settings
from gptgolem.actions import (
    ask_human_action
)


class JustDoerRunner:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.known_actions = {
            'ask_human': ask_human_action,
        }

    def __call__(self, action: dict) -> str:
        for key in action:
            if key not in self.known_actions:
                print(f"Unknown action: {key}")
                return ''
            action_fn = self.known_actions[key]
            kwargs = action[key]
            result = action_fn(**kwargs)
        return result
