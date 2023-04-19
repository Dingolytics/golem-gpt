from typing import Tuple
from gptgolem.settings import Settings
from ..http import http_request
from .history import History


class Dialog:
    """A dialog with the OpenAI API."""

    def __init__(self, settings: Settings, history: History) -> None:
        """Initialize the dialog."""
        self.completions_url = 'https://api.openai.com/v1/chat/completions'
        self.headers = {
            'authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'openai-organization': settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.history = history

    def send_request(self, *, url, method, json=None) -> dict:
        """Send a request to the OpenAI API."""
        return http_request(
            url=url, method=method, headers=self.headers, json=json
        )

    def send_message(
        self, content, temperature: float = 0.2, max_tokens: int = 0
    ) -> Tuple[str, list]:
        """Send a message to the dialog and return the reply."""
        messages = self.history.messages.copy()
        messages.append({"role": "user", "content": content})
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
        }
        if max_tokens:
            payload.update({'max_tokens': max_tokens})
        result = self.send_request(
            url=self.completions_url, method='POST', json=payload
        )
        reply = result['choices'][0]['message']
        chat_id = result['id']
        messages.append(reply)
        self.history.chat_id = chat_id
        self.history.messages = messages
        return (chat_id, messages)

    def get_last_message(self) -> str:
        """Get the last message from the dialog."""
        return self.history.messages[-1]['content']
