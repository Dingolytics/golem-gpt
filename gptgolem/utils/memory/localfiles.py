from json import load as json_load, dump as json_dump
from pathlib import Path
from .base import BaseMemory


class LocalFilesMemory(BaseMemory):
    def __init__(self, root_dir: Path) -> None:
        super().__init__()
        self.config['root_dir'] = root_dir

    @property
    def root_dir(self) -> Path:
        return self.config['root_dir']

    def spawn(self, key: str) -> 'LocalFilesMemory':
        """Spawn a fresh memory instance."""
        isinstance = LocalFilesMemory(self.root_dir)
        isinstance.load(key)
        return isinstance

    def load_file(self, filename: str, default: object) -> list:
        """Load JSON data from a local file."""
        assert self.key
        path = self.root_dir / self.key / filename
        if path.exists():
            with path.open() as file:
                return json_load(file)
        return default

    def save_file(self, filename: str, data: object) -> None:
        """Save JSON data to a local file."""
        assert self.key
        path = self.root_dir / self.key / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as file:
            json_dump(data, file, indent=2, ensure_ascii=False)

    def load_messages(self) -> list:
        """Load the chat history from a local file."""
        return self.load_file('messages.json', [])

    def save_messages(self) -> None:
        """Save the chat history to a local file."""
        self.save_file('messages.json', self.messages)

    def load_goals(self) -> list:
        """Load the goals from a local file."""
        return self.load_file('job.json', {}).get('goals', [])

    def save_goals(self) -> None:
        """Save the goals to a local file."""
        return self.save_file('job.json', {'goals': self.goals})
