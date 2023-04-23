from golemgpt.utils import console
from golemgpt.settings import Settings
from golemgpt.memory import BaseMemory
from golemgpt.utils.http import http_request
from .base import BaseCognitron


class OpenAICognitron(BaseCognitron):
    DEFAULT_NAME = 'OpenAI'
    MAX_TOKENS = 0
    TEMPERATURE = 0.1
    COMPLETIONS_URL = 'https://api.openai.com/v1/chat/completions'

    def __init__(
        self, settings: Settings, memory: BaseMemory, **options
    ) -> None:
        super().__init__(settings, memory, **options)
        self.headers = {
            'authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'openai-organization': settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.memory = memory

    def communicate(self, message: str, **options) -> str:
        """Communicate with the OpenAI and return the reply."""
        max_tokens = options.get('max_tokens', self.MAX_TOKENS)
        temperature = options.get('temperature', self.TEMPERATURE)
        messages = self.memory.messages.copy()
        messages.append({'role': 'user', 'content': message})
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
        }
        if max_tokens:
            payload.update({'max_tokens': max_tokens})

        result = http_request(
            url=self.COMPLETIONS_URL, method='POST',
            headers=self.headers, json=payload
        )
        reply = result['choices'][0]['message']

        messages.append(reply)
        self.memory.messages = messages
        self.memory.save()

        reply_text = self.get_last_message()
        console.message(self.name, reply_text)
        return reply_text
