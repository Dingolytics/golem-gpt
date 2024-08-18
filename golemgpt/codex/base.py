from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings


class BaseCodex:
    def __init__(
        self, settings: Settings, memory: BaseMemory
    ) -> None:
        self.memory = memory
        self.settings = settings

    def align_actions(self, action_plan: list) -> str:
        raise NotImplementedError()
