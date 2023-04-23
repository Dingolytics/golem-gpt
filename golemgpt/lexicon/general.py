from re import compile as re_compile, DOTALL
from typing import List
from json import loads as json_loads, JSONDecodeError
from golemgpt.utils import console
from golemgpt.utils.exceptions import ParseActionsError
from .prompts import (
    INSTRUCTIONAL_PROMPT, OUTPUT_FORMAT_PROMPT, KNOWN_ACTIONS_PROMT,
    CHECK_COMPLETION_PROMPT, INITIALIZER_REPLY_EXAMPLE,
)


class GeneralLexicon:
    role_model_prompt: str = ""

    # Not-a-JSON naive preamble regex:
    naive_preamble_re = re_compile(r'([^\[\{]*)', DOTALL)

    def goal_prompt(self, goal: str) -> str:
        goal = f"{goal.strip().rstrip('.')}. Then finish the job."
        return f"The goal is: {goal}"

    def yesno_prompt(self, question: str) -> str:
        return f"Answer 'yes' or 'no'. {question}"

    def action_result_prompt(self, action: str, result: str) -> str:
        return f'Completed "{action}" with result:\n{result}'

    def remind_format_prompt(self) -> str:
        return 'If finished, just use a single "finish_job" action.'

    def guess_finish_prompt(self, reply: str) -> str:
        preamble = self.lexicon.find_preamble(reply)
        statement = preamble or reply
        return (
            "Does the following mean current job is finished "
            "(optional ask to start a new one)?"
            f"\n\n{statement}"
        )

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

    def find_preamble(self, reply: str) -> str:
        preamble = self.naive_preamble_re.search(reply)
        if preamble:
            return preamble.group()
        return ''

    def parse_reply(self, reply: str) -> List[dict]:
        """Parse the reply into an action plan."""
        console.debug(f"Parse plan:\n{reply}\n")

        # Remove not-a-JSON preamble, sometimes JSON is
        # prepended with some text, like "Here is your JSON:"
        preamble = self.find_preamble(reply)
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
