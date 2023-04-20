from typing import Any, Dict
from ..http import http_request
from .settings import Settings


class ImagePrompt:
    def __init__(self, settings: Settings) -> None:
        """Initialize the prompt."""
        self.generations_url = 'https://api.openai.com/v1/chat/completions'
        self.settings = settings
        self.headers = {
            'authorization': f'Bearer {self.settings.OPENAI_API_KEY}',
            'openai-organization': self.settings.OPENAI_ORG_ID,
        }
        self.size = self.settings.OPENAI_IMAGE_SIZE

    def send_message(
        self, prompt: str, n: int = 1, size: str = ''
    ) -> Dict[str, Any]:
        """Send a message to the dialog and return the reply."""
        return http_request(
            url=self.generations_url, method='POST', headers=self.headers,
            json={'prompt': prompt, 'size': (size or self.size), 'n': n}
        )
