from json import load as json_load
from pathlib import Path

from .base import BaseMemory


class LocalFilesMemory(BaseMemory):
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir

    def load_messages(self) -> list:
        """Load the chat history from a local file."""
        assert self.key
        path = self.root_dir / self.key / 'messages.json'
        if path.exists():
            with path.open() as file:
                return json_load(file)
        return []
