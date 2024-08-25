from json import loads as json_loads, JSONDecodeError

from golemgpt.lexicon import GeneralLexicon, Reply
from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings, Verbosity
from golemgpt.utils import console
from golemgpt.utils.exceptions import ParseActionsError
from golemgpt.utils.http import http_request
from .base import BaseCognitron


class OpenAITextCognitron(BaseCognitron):
    """
    Cognitron powered by OpenAI API with plain text communication.

    Response format and actions list are not enforced but provided with
    initial prompts. Extra heuristics required to process outputs, e.g.
    while converting response to the list of actions.

    Cons: results are less predictable, harder to manage, and debug.
    Pros: approach is more flexible and could be applied to other models
    that does not support explicit tools and output formats definition.

    """

    DEFAULT_NAME = "OpenAI-Text"
    MAX_TOKENS = 0
    TEMPERATURE = 0.1
    COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
    LEXICON_CLASS = GeneralLexicon

    def __init__(
        self,
        settings: Settings,
        memory: BaseMemory,
        verbosity: Verbosity = Verbosity.NORMAL,
        **options
    ) -> None:
        super().__init__(settings, memory, **options)
        self.headers = {
            "authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "openai-organization": settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.memory = memory
        self.verbosity = verbosity

    def communicate(self, message: str, **options) -> Reply:
        """Communicate with the OpenAI and return the reply."""
        max_tokens = options.get("max_tokens", self.MAX_TOKENS)
        temperature = options.get("temperature", self.TEMPERATURE)
        messages = self.memory.messages.copy()
        messages.append({"role": "user", "content": message})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload.update({"max_tokens": max_tokens})

        result = http_request(
            url=self.COMPLETIONS_URL,
            method="POST",
            headers=self.headers,
            json=payload,
        )
        reply = result["choices"][0]["message"]

        # Update history
        messages.append(reply)
        self.memory.messages = messages
        self.memory.save()

        # Print console output
        reply_text = self.get_last_message()

        if self.verbosity >= Verbosity.COMPACT:
            console.message(self.name, reply_text, tags=["reply"])

        return Reply(text=reply_text)

    def plan_actions(self, prompt: str, attempt: int = 0) -> list[dict]:
        """
        Plan actions based on the prompt using naive actions parsing.

        As we communicate the expected format in we'll try to parse actions
        from JSON response. It also could contain non-JSON preamble, which
        we try to detect and truncate.

        """
        if self.verbosity >= Verbosity.COMPACT:
            console.message(self.name, prompt, tags=["prompt"])

        reply = self.communicate(prompt)
        reply_text = reply.text
        console.debug(f"Parse plan:\n{reply_text}\n")

        # Remove not-a-JSON preamble, sometimes JSON is
        # prepended with some text, like "Here is your JSON:"
        preamble = self.lexicon.find_preamble(reply_text)
        if preamble:
            reply_text = reply_text[len(preamble) :]
            console.debug(f"Parse plan (trunc.):\n{reply_text}\n")

        reply_text = reply_text.strip()
        if not reply_text:
            raise ParseActionsError("JSON not found", reply_text)

        try:
            parsed = json_loads(reply_text)
        except JSONDecodeError as exc:
            raise ParseActionsError(exc.msg, reply_text) from exc

        if isinstance(parsed, dict):
            parsed = [parsed]

        return parsed
