from typing import Any, Dict
from ..http import http_request
from .settings import Settings


class ImagePrompt:
    def __init__(self, settings: Settings) -> None:
        """Initialize the prompt."""
        self.settings = settings

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
        self, prompt: str, n: int = 1, size: str = ''
    ) -> Dict[str, Any]:
        """Send a message to the dialog and return the reply."""
        size = size or self.settings.OPENAI_IMAGE_SIZE
        result = self.send_request(
            url='https://api.openai.com/v1/images/generations', method='POST',
            json={
                'prompt': prompt,
                'n': n,
                'size': size,
            }
        )
        return result
