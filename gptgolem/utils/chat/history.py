from pathlib import Path
from json import load as json_load, dump as json_dump
# from pprint import pprint
from pydantic import BaseModel


class History(BaseModel):
    """A chat history."""
    key: str
    chat_id: str = ''
    messages: list = []
    root: str = './history'

    @property
    def is_empty(self) -> bool:
        """Check if the chat history is empty."""
        return not self.messages

    def get_dir(self) -> Path:
        """Get the path to the chat history directory."""
        return Path(f'{self.root}')

    def get_path(self):
        """Get the path to the chat history file."""
        return Path(f'{self.root}/{self.key}.json')

    def print_message(self, item: dict) -> None:
        """Print the last message in the chat history."""
        role = item['role'].capitalize()
        print(f"{role}:")
        print("-" * (1 + len(role)))
        print(item['content'].strip())
        print("\n")

    def print_all_messages(self):
        """Print the chat history."""
        if self.is_empty:
            print("No messages.")
            return
        for item in self.messages:
            self.print_message(item)

    def print_last_message(self):
        """Print the last message in the chat history."""
        if not self.is_empty:
            self.print_message(self.messages[-1])

    def dump_message(self, idx: int = -1):
        """Dump the last message in the chat history to a file."""
        if len(self.messages) == 0:
            return
        if idx < 0:
            idx = len(self.messages) + idx
        path = Path(f'{self.root}/{self.key}/{idx}.txt')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as file:
            file.write(self.messages[idx]['content'].strip())

    def load(self) -> None:
        """Load the chat history from a file."""
        assert self.key
        self.get_dir().mkdir(parents=True, exist_ok=True)
        path = self.get_path()
        if path.exists():
            with path.open() as file:
                data = json_load(file)
                self.chat_id = data['chat_id']
                self.messages = data['messages']

    def save(self) -> None:
        """Save the chat history to a file."""
        assert self.key
        self.get_dir().mkdir(parents=True, exist_ok=True)
        path = self.get_path()
        with path.open(mode='w') as file:
            data = {
                'chat_id': self.chat_id,
                'messages': self.messages
            }
            json_dump(data, file, indent=2)
