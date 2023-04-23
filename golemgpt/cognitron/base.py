from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings


class BaseCognitron:
    DEFAULT_NAME = 'Cognitron'

    def __init__(
        self, settings: Settings, memory: BaseMemory, name: str = ''
    ) -> None:
        self.settings = settings
        self.memory = memory
        self.name = name or self.DEFAULT_NAME

    def communicate(self, message: str, **options) -> str:
        """Communicate with the Cognitron and return the reply."""
        raise NotImplementedError()

    def ask_yesno(self, message: str, **options) -> str:
        """Ask the Cognitron a yes/no question and return the reply."""
        yesno = self.communicate(message)
        return yesno.lower().startswith('yes')

    def get_last_message(self) -> str:
        """Get the last message from the dialog with the Cognitron."""
        return self.memory.messages[-1]['content']
