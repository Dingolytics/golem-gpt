import json
from golemgpt.lexicon import BaseLexicon
from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings


class BaseCognitron:
    DEFAULT_NAME = 'Cognitron'

    LEXICON_CLASS = BaseLexicon

    def __init__(
        self, settings: Settings, memory: BaseMemory, name: str = ''
    ) -> None:
        self.settings = settings
        self.memory = memory
        self.name = name or self.DEFAULT_NAME
        self.lexicon = self.LEXICON_CLASS()

    def communicate(self, message: str, **options) -> str:
        """Communicate with the Cognitron and return the reply."""
        raise NotImplementedError()

    def ask_yesno(self, message: str, **options) -> bool:
        """Ask the Cognitron a yes/no question and return the reply."""
        yesno = self.communicate(message)
        return self.lexicon.guess_yesno(yesno)

    def get_last_message(self) -> str:
        """Get the last message from the dialog with the Cognitron."""
        message = self.memory.messages[-1]
        if message.get('tool_calls'):
            return json.dumps(message.get('tool_calls'))
        return message['content']
