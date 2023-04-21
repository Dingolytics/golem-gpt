from typing import Tuple
from golemgpt.settings import Settings
from golemgpt.utils.http import http_request
from golemgpt.utils.memory import BaseMemory


class Dialog:
    """A dialog with the OpenAI API."""

    def __init__(self, settings: Settings, memory: BaseMemory) -> None:
        """Initialize the dialog."""
        self.completions_url = 'https://api.openai.com/v1/chat/completions'
        self.headers = {
            'authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'openai-organization': settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.memory = memory

    def send_message(
        self, content, temperature: float = 0, role: str = 'user',
        max_tokens: int = 0
    ) -> Tuple[str, list]:
        """Send a message to the dialog and return the reply."""
        # TODO: Store the chat ID in the memory.
        # TODO: Store more messages context in the memory.
        messages = self.memory.messages.copy()
        messages.append({"role": role, "content": content})
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
        }
        if max_tokens:
            payload.update({'max_tokens': max_tokens})
        result = http_request(
            url=self.completions_url, method='POST',
            headers=self.headers, json=payload
        )
        reply = result['choices'][0]['message']
        # chat_id = result['id']
        messages.append(reply)
        self.memory.messages = messages
        return '', messages
        # return (chat_id, messages)

    def get_last_message(self) -> str:
        """Get the last message from the dialog."""
        return self.memory.messages[-1]['content']
