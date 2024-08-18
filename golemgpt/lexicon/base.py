from re import compile as re_compile, DOTALL

from pydantic import BaseModel

from golemgpt.utils.exceptions import UnknownReplyFormat


class Reply(BaseModel):
    """General representation of reploy from Cognitron."""

    text: str = ""
    actions: list = []


class BaseLexicon:
    # Not-a-JSON naive preamble regex:
    naive_preamble_re = re_compile(r'([^\[\{]*)', DOTALL)

    def initializer_prompt(self) -> str:
        return ""

    def goal_prompt(self, goal: str) -> str:
        tools_hint = (
            "NOTES: Use actions provided. "
            "Ask credentials from user if needed, be specific for which "
            "API endpoint you'll use it (exact address needed)."
        )
        goal = goal.strip().rstrip('.')
        return f"The goal is: {goal}.\n\n{tools_hint}"

    def yesno_prompt(self, question: str) -> str:
        return f"Answer 'yes' or 'no'. {question}"

    def action_result_prompt(self, action: str, result: str) -> str:
        return f"Completed '{action}' with result:\n{result}"

    def remind_format_prompt(self) -> str:
        return "If finished, just use a single 'finish_job' action."

    def guess_finish_prompt(self, reply: str) -> str:
        preamble = self.find_preamble(reply)
        statement = preamble or reply
        return (
            "Does the following mean current job is finished "
            "(optional ask to start a new one)?"
            f"\n\n{statement}"
        )

    def guess_yesno(self, reply: Reply) -> bool:
        """Guess if the reply is yes or no."""
        if not reply.text:
            raise UnknownReplyFormat(f"{reply}")
        return reply.text.lower().startswith("yes")

    def initializer_history(self) -> list:
        prompt = self.initializer_prompt()
        return [{"role": "user", "content": prompt}]

    def find_preamble(self, reply: str) -> str:
        preamble = self.naive_preamble_re.search(reply)
        if preamble:
            return preamble.group()
        return ""
