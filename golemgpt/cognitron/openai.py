import inspect
from json import loads as json_loads
from typing import Any, Callable

from golemgpt.handlers.base import BaseHandler
from golemgpt.lexicon import BaseLexicon, Reply
from golemgpt.memory import BaseMemory
from golemgpt.settings import Settings, Verbosity
from golemgpt.types import ActionFn
from golemgpt.utils import console
from golemgpt.utils.exceptions import UnknownAction, UnknownReplyFormat
from golemgpt.utils.http import http_request_as_json
from .base import BaseCognitron


class OpenAIWithToolsLexicon(BaseLexicon):
    def initializer_prompt(self) -> str:
        return (
            "You are smart bot that can fulfill high-level tasks "
            "using API calls and other utilities."
        )

    def goal_prompt(self, goal: str) -> str:
        tools_hint = (
            "NOTES: Use tools provided. Prefer public APIs that do not "
            "require credentials. Ask credentials from user if needed, "
            "be specific for which API endpoint you'll use it (exact "
            "address needed)."
        )
        goal = goal.strip().rstrip(".")
        return f"The goal is: {goal}.\n\n{tools_hint}"

    def yesno_prompt(self, question: str) -> str:
        return f"Reply 'yes' or 'no'. {question}"

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
            console.error(f"Unknown action: {item}")

        try:
            args = json_loads(item["function"]["arguments"])
        except KeyError:
            pass

        return (name, args)


def extract_fn_params_jsonschema(action_fn: Callable):
    def _extract_type(annotation: Any) -> str:
        if hasattr(annotation, "__args__"):
            return annotation.__args__[0].__name__
        return annotation.__name__

    def _json_type(name: str) -> str:
        types_map = {
            "str": "string",
            "float": "number",
            "int": "number",
            "bool": "boolean",
            "dict": "object",
        }
        return types_map.get(name, "object")

    signature = inspect.signature(action_fn)
    parameters: dict[str, str | dict[str, Any]] = {}

    if signature.parameters:
        parameters = {
            "type": "object",
            "properties": {
                name: {"type": _json_type(_extract_type(arg.annotation))}
                for name, arg in signature.parameters.items()
            },
        }

    return parameters


class OpenAIToolsCognitron(BaseCognitron):
    """
    Cognitron powered by OpenAI API with 'tools' feature.

    Instead of trying to parse action plan naively from plain JSON we
    provide the list of tools during communication.

    The main difference from `OpenAINaiveCognitron` is that we always
    get only one next action instead of multi-step action plan.
    """

    DEFAULT_NAME = "OpenAI-Tools"
    MAX_TOKENS = 0
    TEMPERATURE = 0.1
    COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
    LEXICON_CLASS = OpenAIWithToolsLexicon

    def __init__(
        self,
        settings: Settings,
        memory: BaseMemory,
        verbosity: Verbosity = Verbosity.NORMAL,
        **options,
    ) -> None:
        super().__init__(settings, memory, **options)
        self.headers = {
            "authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "openai-organization": settings.OPENAI_ORG_ID,
        }
        self.model = settings.OPENAI_MODEL
        self.tools = self.parse_actions_to_tools(self.actions)
        self.verbosity = verbosity

    @classmethod
    def parse_actions_to_tools(
        cls, actions: dict[str, ActionFn | type]
    ) -> list[dict[str, Any]]:
        """
        Parse known actions (callables with possible side-effects) to tools.

        'Tools' is the new feature of OpenAI's communication model. They can
        reply with the list of tools to use instead of plain text reply.
        """
        tools = []

        def _extract_type(annotation: Any) -> str:
            if hasattr(annotation, "__args__"):
                return annotation.__args__[0].__name__
            return annotation.__name__

        def _json_type(name: str) -> str:
            types_map = {
                "str": "string",
                "float": "number",
                "int": "number",
                "bool": "boolean",
                "dict": "object",
            }
            return types_map.get(name, "object")

        for key in actions:
            action_fn = actions[key]

            if isinstance(action_fn, type):
                assert issubclass(action_fn, BaseHandler)
                parameters = action_fn.get_params_jsonschema()
                description = action_fn.get_description()
            else:
                parameters = extract_fn_params_jsonschema(action_fn)
                description = actions[key].__doc__ or " ".join(key.split("_"))

            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": key,
                        "description": description,
                        "parameters": parameters,
                    },
                }
            )

        return tools

    def parse_tool_call(self, item: dict) -> tuple[str, dict]:
        """
        Extract the function name and its arguments from a tool call item.
        """
        assert isinstance(self.lexicon, OpenAIWithToolsLexicon)
        return self.lexicon.parse_tool_call(item)

    def plan_actions(self, prompt: str, attempt: int = 0) -> list[dict]:
        """
        Plan actions based on the prompt using with use of tools.

        We communicate the list of tools available via OpenAI call. We get
        the list of suggested calls in the reply. Actually it's a single-item
        list because that's how OpenAI's tools feature works currently.
        """
        if self.verbosity >= Verbosity.COMPACT:
            console.message(self.name, prompt, tags=["prompt"])
        reply = self.communicate(prompt)
        actions: list[dict] = []

        for item in reply.actions:
            name, args = self.parse_tool_call(item)
            if name:
                actions.append({name: args})

        if not actions:
            raise UnknownAction(f"{reply}")

        return actions

    def communicate(self, message: str, **options) -> Reply:
        """
        Communicate with the OpenAI and return the reply.
        """
        max_tokens = options.get("max_tokens", self.MAX_TOKENS)
        temperature = options.get("temperature", self.TEMPERATURE)
        messages = self.memory.messages.copy()

        # If previous message was a tool call then we should provide
        # tool response in the specific format.
        tool_call_id = ""
        if messages:
            last_message = messages[-1]
            if "tool_calls" in last_message:
                last_tool_call = last_message["tool_calls"][0]
                tool_call_id = last_tool_call.get("id") or ""

        if tool_call_id:
            next_message = {
                "role": "tool",
                "content": message,
                "tool_call_id": tool_call_id,
            }
        else:
            next_message = {"role": "user", "content": message}
        messages.append(next_message)

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "tools": self.tools,
            # TODO: Implement parallel tool calls option
            "parallel_tool_calls": False,
            "tool_choice": "required",
        }
        if max_tokens:
            payload.update({"max_tokens": max_tokens})

        result = http_request_as_json(
            url=self.COMPLETIONS_URL,
            method="POST",
            headers=self.headers,
            json=payload,
        )
        reply = result["choices"][0]["message"]
        actions = reply["tool_calls"]

        # Update history
        messages.append(reply)
        self.memory.messages = messages
        self.memory.save()

        # Print console output
        reply_text = ""
        for item in actions:
            arguments = json_loads(item["function"]["arguments"])
            arguments_text = " | ".join(
                [f"{k}={v}" for k, v in arguments.items()]
            )
            reply_text += f'- {item["function"]["name"]}({arguments_text})\n'
        if self.verbosity >= Verbosity.COMPACT:
            console.message(self.name, reply_text.strip(), tags=["reply"])

        return Reply(actions=actions)
