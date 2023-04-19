from typing import Optional
from gptgolem.utils.chat.history import History


class BaseMemory:
    key: str = ''
    history: Optional[History] = None

    def load(self, key: str) -> None:
        """Load the job configuration and history."""
        self.key = key
        messages = self.load_messages()
        self.history = History(key=self.key, messages=messages)

    def load_messages(self) -> list:
        raise NotImplementedError()
