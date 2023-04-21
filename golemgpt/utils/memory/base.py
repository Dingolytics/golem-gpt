from pydantic import BaseModel


class BaseMemory(BaseModel):
    key: str = ''
    goals: list = []
    messages: list = []
    config: dict = {}

    def spawn(self, key: str) -> 'BaseMemory':
        """Spawn a fresh memory instance."""
        cls = self.__class__
        instance = cls(config=self.config)
        instance.load(key)
        return instance

    @property
    def is_history_empty(self) -> bool:
        return len(self.messages) == 0

    def load(self, key: str) -> None:
        """Load the job configuration and history."""
        self.key = key
        self.messages = self.load_messages()
        self.goals = self.load_goals()

    def save(self) -> None:
        """Save the job configuration and history."""
        self.save_messages()
        self.save_goals()

    def load_messages(self) -> list:
        raise NotImplementedError()

    def save_messages(self) -> None:
        raise NotImplementedError()

    def load_goals(self) -> list:
        raise NotImplementedError()

    def save_goals(self) -> None:
        raise NotImplementedError()

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

    def print_message(self, item: dict) -> None:
        """Print the last message in the chat history."""
        role = item['role'].capitalize()
        print(f"{role}:")
        print("-" * (1 + len(role)))
        print(item['content'].strip())
        print("\n")
