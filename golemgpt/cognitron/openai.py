import inspect
from json import loads as json_loads, JSONDecodeError
from typing import Any, Callable

from golemgpt.lexicon import BaseLexicon, GeneralLexicon, Reply
from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings
from golemgpt.utils import console
from golemgpt.utils.exceptions import (
    ParseActionsError,
    UnknownAction,
    UnknownReplyFormat
)
from golemgpt.utils.http import http_request
from .base import BaseCognitron


class OpenAINaiveCognitron(BaseCognitron):
    """
    Naive implementation without explicit tools definition.

    Response format and actions list are not enforced but provided with
    initial prompts. Extra heuristics required to process outputs, e.g.
    while converting response to the list of actions.

    Cons: results are less predictable, harder to manage, and debug.
    Pros: approach is more flexible and could be applied to other models
    that does not support explicit tools and output formats definition.

    """
    DEFAULT_NAME = 'OpenAI-Naive'
    MAX_TOKENS = 0
    TEMPERATURE = 0.1
    COMPLETIONS_URL = 'https://api.openai.com/v1/chat/completions'
    LEXICON_CLASS = GeneralLexicon

    def __init__(
        self, settings: Settings, memory: BaseMemory, **options
    ) -> None:
        super().__init__(settings, memory, **options)
        self.headers = {
            'authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'openai-organization': settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.memory = memory

    def communicate(self, message: str, **options) -> Reply:
        """Communicate with the OpenAI and return the reply."""
        max_tokens = options.get('max_tokens', self.MAX_TOKENS)
        temperature = options.get('temperature', self.TEMPERATURE)
        messages = self.memory.messages.copy()
        messages.append({'role': 'user', 'content': message})
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
        }
        if max_tokens:
            payload.update({'max_tokens': max_tokens})

        result = http_request(
            url=self.COMPLETIONS_URL, method='POST',
            headers=self.headers, json=payload
        )
        reply = result['choices'][0]['message']

        messages.append(reply)
        self.memory.messages = messages
        self.memory.save()

        reply_text = self.get_last_message()
        console.message(self.name, reply_text)

        return Reply(text=reply_text)

    def plan_actions(self, prompt: str, attempt: int = 0) -> list[dict]:
        """
        Plan actions based on the prompt using naive actions parsing.

        As we communicate the expected format in we'll try to parse actions
        from JSON response. It also could contain non-JSON preamble, which
        we try to detect and truncate.

        """
        console.message(self.name, prompt)
        reply = self.communicate(prompt)

        console.debug(f"Parse plan:\n{reply}\n")

        # Remove not-a-JSON preamble, sometimes JSON is
        # prepended with some text, like "Here is your JSON:"
        preamble = self.lexicon.find_preamble(reply)
        if preamble:
            reply = reply[len(preamble):]
            console.debug(f"Parse plan (trunc.):\n{reply}\n")

        reply = reply.strip()
        if not reply:
            raise ParseActionsError("JSON not found", reply)

        try:
            parsed = json_loads(reply)
        except JSONDecodeError as exc:
            raise ParseActionsError(exc.msg, reply) from exc

        if isinstance(parsed, dict):
            parsed = [parsed]

        return parsed


class OpenAIWithToolsLexicon(BaseLexicon):

    def goal_prompt(self, goal: str) -> str:
        tools_hint = (
            "NOTES: Use tools provided. "
            "Ask credentials from user if needed first."
        )
        goal = goal.strip().rstrip('.')
        return f"The goal is: {goal}. {tools_hint}"

    def yesno_prompt(self, question: str) -> str:
        return f"'yes' or 'no'?. {question}"

    def action_result_prompt(self, action: str, result: str) -> str:
        return f'Completed "{action}" with result:\n{result}'

    def guess_yesno(self, reply: Reply) -> bool:
        """Define by actions in the reply if it's yes or no ."""

        for item in reply.actions:
            name, args = self.parse_tool_call(item)
            if name == "reply_yes_or_no":
                return str(args.get("answer")).lower() in {"yes"}

        raise UnknownReplyFormat(f"{reply}")

    def parse_tool_call(self, item: dict) -> tuple[str, dict]:
        args = {}
        name = ""

        try:
            name = item["function"]["name"]
        except KeyError:
            console.info(f"Unknown action: {item}")

        try:
            args = json_loads(item["function"]["arguments"])
        except KeyError:
            pass

        return (name, args)


class OpenAIWithToolsCognitron(BaseCognitron):
    """
    Cognitron powered by OpenAI API with 'tools' feature.

    Instead of trying to parse action plan naively from plain JSON we
    provide the list of tools during communication.

    The main difference from `OpenAINaiveCognitron` is that we always
    get only one next action instead of multi-step action plan.

    """
    DEFAULT_NAME = 'OpenAI-Tools'
    MAX_TOKENS = 0
    TEMPERATURE = 0.1
    COMPLETIONS_URL = 'https://api.openai.com/v1/chat/completions'
    LEXICON_CLASS = OpenAIWithToolsLexicon

    def __init__(
        self, settings: Settings, memory: BaseMemory, **options,
    ) -> None:
        super().__init__(settings, memory, **options)
        self.headers = {
            'authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'openai-organization': settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.memory = memory
        self.tools = self.parse_actions_to_tools(self.actions)

    @classmethod
    def parse_actions_to_tools(
        cls, actions: dict[str, Callable]
    ) -> list[dict[str, Any]]:
        """
        Parse known actions (callables with possible side-effects) to tools.

        'Tools' is the new feature of OpenAI's communication model. They can
        reply with the list of tools to use instead of plain text reply.
        """
        tools = []

        def _json_type(name: str) -> str:
            types_map = {
                'str': 'string',
                'float': 'number',
                'int': 'number',
                'bool': 'boolean',
                # 'list': 'array',
                'dict': 'object',
            }
            return types_map.get(name, 'object')

        for key in actions:
            signature = inspect.signature(actions[key])
            if signature.parameters:
                parameters = {
                    'type': 'object',
                    'properties': {
                        name: {
                            'type': _json_type(arg.annotation.__name__)
                        } for name, arg in signature.parameters.items()
                    }
                }
            else:
                parameters = {}
            description = actions[key].__doc__ or ' '.join(key.split('_'))
            tools.append({
                'type': 'function',
                'function': {
                    'name': key,
                    'description': description,
                    'parameters': parameters,
                },
            })
        return tools

    def plan_actions(self, prompt: str, attempt: int = 0) -> list[dict]:
        """
        Plan actions based on the prompt using with use of tools.

        We communicate the list of tools available via OpenAI call. We get
        the list of suggested calls in the reply. Actually it's a single-item
        list because that's how OpenAI's tools feature works currently.

        """
        console.message(self.name, prompt)
        reply = self.communicate(prompt)
        actions: list[dict] = []

        for item in reply.actions:
            name, args = self.lexicon.parse_tool_call(item)
            if name:
                actions.append({name: args})

        if not actions:
            raise UnknownAction(f"{reply}")

        return actions

    def communicate(self, message: str, **options) -> Reply:
        """Communicate with the OpenAI and return the reply."""
        max_tokens = options.get('max_tokens', self.MAX_TOKENS)
        temperature = options.get('temperature', self.TEMPERATURE)
        messages = self.memory.messages.copy()
        messages.append({'role': 'user', 'content': message})
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            # 'response_format': {'type': 'json_object'},
            'tools': self.tools,
            'tool_choice': 'required'
        }
        if max_tokens:
            payload.update({'max_tokens': max_tokens})

        result = http_request(
            url=self.COMPLETIONS_URL, method='POST',
            headers=self.headers, json=payload
        )
        reply = result['choices'][0]['message']

        messages.append(reply)
        self.memory.messages = messages
        self.memory.save()

        reply_text = self.get_last_message()
        console.message(self.name, reply_text)

        return Reply(actions=reply['tool_calls'])
