
from golemgpt.utils import console
from .base import BaseCodex


class UnawareCodex(BaseCodex):
    def align_actions(self, action_plan: list) -> str:
        console.debug(f"Naively approve actions: {action_plan}")
        return True
