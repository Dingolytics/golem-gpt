from .base import BaseLexicon
from .prompts import (
    INSTRUCTIONAL_PROMPT,
    OUTPUT_FORMAT_PROMPT,
    KNOWN_ACTIONS_PROMT,
    CHECK_COMPLETION_PROMPT,
    INITIALIZER_REPLY_EXAMPLE,
)


class GeneralLexicon(BaseLexicon):
    role_model_prompt: str = ""

    def initializer_prompt(self) -> str:
        return (
            f"{self.role_model_prompt}\n\n"
            f"{INSTRUCTIONAL_PROMPT}\n\n"
            f"{OUTPUT_FORMAT_PROMPT}\n\n"
            f"{KNOWN_ACTIONS_PROMT}\n\n"
            f"{CHECK_COMPLETION_PROMPT}\n\n"
        ).strip()

    def initializer_history(self) -> list:
        prompt = self.initializer_prompt()
        reply = INITIALIZER_REPLY_EXAMPLE
        return [
            {'role': 'user', 'content': prompt},
            {'role': 'assistant', 'content': reply},
        ]
