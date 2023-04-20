from typing import Tuple


class AlwaysAskRunner:
    """A runner that asks for confirmation before running an action."""

    def __call__(self, action: dict) -> Tuple[str, str]:
        yes = input(f"Press Y to run action: {action}")
        if yes.lower() != 'y':
            return '', ''
        super().__call__(action)
