from json import loads as json_loads, JSONDecodeError
from typing import Callable, List
from golemgpt.settings import Settings
from golemgpt.utils import console, genkey
from golemgpt.utils.memory.base import BaseMemory
from golemgpt.utils.chat.dialog import Dialog
from golemgpt.runners import JustDoRunner
from golemgpt.actions import JobFinished, JobRejected
from ._defs import WRONG_FORMAT_PROMPT


def load_roles(settings: Settings) -> dict:
    return {}


def load_runner(settings: Settings) -> Callable:
    return JustDoRunner(settings)


class General:
    prompt = ''

    # TODO: Implement review_action_plan() ?
    # TODO: Spawn a new Golem to make parseable action plan from the reply ?

    def __init__(
        self, *, goals: List[str], job_key: str, memory: BaseMemory,
        settings: Settings, roles = load_roles, runner = load_runner
    ) -> None:
        self.job_key = job_key
        self.memory = memory
        self.settings = settings
        self.completed = []
        self.action_plan = []
        self.goals = goals
        self.roles = roles(settings)
        self.runner = runner(settings)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.job_key})"

    def side_dialog(self, prompt: str) -> str:
        """Spawn a side dialog to interpret the mainline replies."""
        key = f'{self.job_key}.{genkey()}'
        memory = self.memory.spawn(key)
        dialog = Dialog(self.settings, memory)
        console.message('user', prompt)
        dialog.send_message(prompt, temperature=0)
        reply = dialog.get_last_message()
        memory.save()
        console.message('quick', reply)
        return reply

    def guess_yesno(self, question: str) -> bool:
        """Guess if the reply is a yes or no."""
        yesno = self.side_dialog(f"Answer 'yes' or 'no'. {question}")
        return yesno.lower().startswith('y')

    def syncronize(self) -> None:
        console.debug(f"Syncing job state with memory: {self.job_key}")
        if self.memory.is_history_empty:
            self.memory.load(self.job_key)

        if self.goals:
            self.memory.goals = self.goals
        else:
            self.goals = self.memory.goals
            assert self.goals, "Goals not provided, and not found in memory"

        self.memory.save()

    def start_job(self) -> None:
        console.debug(f"Starting job: {self.job_key}")
        self.syncronize()
        prompt = self.get_initial_prompt()
        while True:
            try:
                if prompt:
                    self.update_plan(prompt)
                prompt = self.run_next_action()
            except JobFinished:
                break
            except JobRejected:
                break
        console.debug(f"Job {self.job_key} completed")

    def get_initial_prompt(self) -> List[str]:
        return f"{self.prompt}\n\nThe goal is: {self.goals[-1]}"

    def parse_reply(self, reply: str) -> List[dict]:
        """Parse the reply into an action plan."""
        console.debug(f"Parse plan:\n{reply}\n")
        reply = reply.strip()
        try:
            self.action_plan = json_loads(reply)
        except JSONDecodeError:
            raise
            # Try to parse the last line only
            # lines = reply.splitlines()
            # if len(lines) > 1:
            #     self.parse_plan(lines.pop())
            # else:
            #     raise

    def update_plan(self, prompt: str, attempt: int = 0) -> None:
        """Ask to update the plan based on the prompt."""
        dialog = Dialog(self.settings, self.memory)
        console.message('user', prompt)
        # role = 'system' if self.memory.is_history_empty else 'user'
        dialog.send_message(prompt)
        reply = dialog.get_last_message()
        self.memory.save()
        console.message('golem', reply)
        try:
            self.parse_reply(reply)
        except JSONDecodeError:
            question = (
                "Does the following mean current job is finished"
                f" (optional ask to start a new one)?\n\n{reply}"
            )
            if self.guess_yesno(question):
                raise JobFinished()
            else:
                self.update_plan(WRONG_FORMAT_PROMPT, attempt + 1)

    def run_next_action(self) -> str:
        if self.action_plan:
            action_item = self.action_plan.pop(0)
            action, result = self.runner(action_item, golem=self)
            if not result:
                return ''
            return f'"{action}" completed, result: {result}'
        else:
            raise JobFinished()
