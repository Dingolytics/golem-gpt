from typing import Tuple
from ..http import http_request
from .history import History
from .settings import Settings


class Dialog:
    """A dialog with the OpenAI API."""

    def __init__(self, settings: Settings, history: History) -> None:
        """Initialize the dialog."""
        self.settings = settings
        self.history = history

    def save(self) -> None:
        """Save the dialog history."""
        self.history.save()

    def send_request(self, *, url, method, json=None) -> dict:
        """Send a request to the OpenAI API."""
        headers = {
            'authorization': f'Bearer {self.settings.OPENAI_API_KEY}',
            'openai-organization': self.settings.OPENAI_ORG_ID,
        }
        return http_request(
            url=url, method=method, headers=headers, json=json
        )

    def send_message(
        self, content, temperature: float = 0.2, max_tokens: int = 300
    ) -> Tuple[str, list]:
        """Send a message to the dialog and return the reply."""
        self.history.load()
        messages = self.history.messages.copy()
        messages.append({"role": "user", "content": content})
        result = self.send_request(
            url='https://api.openai.com/v1/chat/completions', method='POST',
            json={
                'model': self.settings.OPENAI_MODEL,
                'messages': messages,
                'temperature': temperature,
                # 'max_tokens': max_tokens,
            }
        )
        reply = result['choices'][0]['message']
        chat_id = result['id']
        messages.append(reply)
        self.history.chat_id = chat_id
        self.history.messages = messages
        return (chat_id, messages)
