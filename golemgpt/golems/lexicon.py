from re import compile as re_compile, DOTALL
from typing import List
from json import dumps as json_dumps, loads as json_loads, JSONDecodeError
from golemgpt.utils import console
from golemgpt.utils.exceptions import ParseActionsError


class GeneralLexicon:
    role_model_prompt: str = ""

    # Not-a-JSON naive preamble regex:
    naive_preamble_re = re_compile(r'([^\[\{]*)', DOTALL)

    def goal_prompt(self, goal: str) -> str:
        goal = f"{goal.strip()} Then finish the job."
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


INSTRUCTIONAL_PROMPT = """
Write a pseudo-code defining a list of actions to execute, so bots could
understand that. You provide a list of actions, bots will execute them
and you will get results.

Bypass already executed actions, use results provided.
""".strip()

INITIALIZER_REPLY_EXAMPLE = json_dumps([
    {'ask_human_input': {'query': 'What is the goal?'}},
]).strip()

# - create_python_script: name, description, in_files, out_files
# - create_shell_script: name, description, in_files, out_files
# - delegate_job: goal, role, in_files, out_files

KNOWN_ACTIONS_PROMT = """
You can use the following actions, higher in the list means
the higher priority:

- get_os_details:
- get_local_date:
- summarize_file: filename, hint, out_filename
- read_file: filename
- write_file: filename, content
- http_download: url, method, headers, body, out_filename
- run_script: name
- ask_human_input: query
- ask_google: query, out_filename
- explain: comment
- reject_job: message
- finish_job: message

Always find a corresponding actions from the list above.
""".strip()

KNOWN_ROLES_PROMT = ""

# KNOWN_ROLES_PROMT = """
# When using a the "delegate_job" action, assume the following roles:

# - "coder" can create function with defined goal, inputs and outputs
# - "admin" can install software on current machine
# """.strip()

# - "devops" can create configuration files for deployment
# - "webdesigner" can create HTML page and save it to the file
# - "artist" can create image and save it to the file
# - "reviewer" can review the code or action and provide feedback

OUTPUT_FORMAT_PROMPT = """
Always use machine readable JSON for every response. Don't add preambles.
Don't be verbose. Use the "explain" action to add thoughts, thanks, etc.

Format:

[
{"action_1": {"param_1": "value_1"}},
{"write_file": {"filename": "hello.txt", "content": "Hello there."}}
]
""".strip()

CHECK_COMPLETION_PROMPT = """
Check if job is completed after each action and respond with "finish_job"
on success.
""".strip()
