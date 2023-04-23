from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings


class BaseCognitron:
    def __init__(self, settings: Settings, memory: BaseMemory) -> None:
        self.settings = settings
        self.memory = memory

    def communicate(self, message: str) -> str:
        raise NotImplementedError()
