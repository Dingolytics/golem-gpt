import inspect
import json
from typing import Any, Callable

from golemgpt.lexicon import BaseLexicon, GeneralLexicon
from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings
from golemgpt.utils import console
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

    def communicate(self, message: str, **options) -> str:
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
        return reply_text


class OpenAIWithToolsLexicon(BaseLexicon):

    def goal_prompt(self, goal: str) -> str:
        # tools_hint = "Respond with JSON list of tools to use."
        tools_hint = "Use tools provided."
        goal = goal.strip().rstrip('.')
        return f"The goal is: {goal}. {tools_hint}"

    def yesno_prompt(self, question: str) -> str:
        return f"'yes' or 'no'?. {question}"

    def guess_yesno(self, reply) -> bool:
        result = json.loads(reply).get('result')
        return result.lower().startswith('yes')

    def action_result_prompt(self, action: str, result: str) -> str:
        return f'Completed "{action}" with result:\n{result}'


class OpenAIWithToolsCognitron(BaseCognitron):
    DEFAULT_NAME = 'OpenAI-Tools'
    MAX_TOKENS = 0
    TEMPERATURE = 0.1
    COMPLETIONS_URL = 'https://api.openai.com/v1/chat/completions'
    LEXICON_CLASS = OpenAIWithToolsLexicon

    def __init__(
        self, settings: Settings, memory: BaseMemory,
        actions: dict[str, Callable], **options,
    ) -> None:
        super().__init__(settings, memory, **options)
        self.headers = {
            'authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'openai-organization': settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.memory = memory
        self.tools = self.parse_actions_to_tools(actions)

    @classmethod
    def parse_actions_to_tools(
        cls, actions: dict[str, Callable]
    ) -> list[dict[str, Any]]:
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
        """Ask to update the plan based on the prompt."""
        console.message(self.name, prompt)
        actions = self.communicate(prompt)
        return actions

    def communicate(self, message: str, **options) -> list[dict]:
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

        return reply['tool_calls']
