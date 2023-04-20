from json import loads as json_loads
from typing import Callable, List
from golemgpt.settings import Settings
from golemgpt.utils import console
from golemgpt.utils.memory.base import BaseMemory
from golemgpt.utils.chat.dialog import Dialog
from golemgpt.runners import JustDoRunner
from golemgpt.actions import JobFinished, JobRejected


def load_roles(settings: Settings) -> dict:
    return {}


def load_runner(settings: Settings) -> Callable:
    return JustDoRunner(settings)


class General:
    prompt = ''

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
                    self.plan_next_actions(prompt)
                prompt = self.run_next_action()
            except JobFinished:
                break
            except JobRejected:
                break
        console.debug(f"Job {self.job_key} completed")

    def get_initial_prompt(self) -> List[str]:
        return f"{self.prompt}\n\nThe goal is: {self.goals[-1]}"

    def plan_next_actions(self, prompt: str) -> None:
        # console.debug(f"Planning next actions after:\n{prompt}\n")
        dialog = Dialog(self.settings, self.memory)
        console.message('user', prompt)
        # role = 'system' if self.memory.is_history_empty else 'user'
        dialog.send_message(prompt)
        reply = dialog.get_last_message()
        console.message('golem', reply)
        console.debug(f"Parsing action plan from reply:\n{reply}\n")
        self.action_plan = json_loads(reply)
        self.memory.save()

    def run_next_action(self) -> str:
        if self.action_plan:
            action_item = self.action_plan.pop(0)
            # print(f"Try running action: {action_item} with {self.runner}")
            action, result = self.runner(action_item, golem=self)
            if not result:
                return ''
            return f"Completed {action}(), result: {result}"
            # return f"Result of '{action}()': {result}"
            # if result and not self.action_plan:
            #     self.plan_next_actions(f"Output of '{action}()': {result}")
        else:
            raise JobFinished()

# TODO: review_action_plan explicitly?
