from json import loads as json_loads
from typing import Callable
from gptgolem.settings import Settings
from gptgolem.utils.memory.base import BaseMemory
from gptgolem.utils.chat.dialog import Dialog
from gptgolem.runners import JustDoRunner
from gptgolem.actions import JobFinished
from ._defs import FINISH_PROMPT


def load_roles(settings: Settings) -> dict:
    return {}


def load_runner(settings: Settings) -> Callable:
    return JustDoRunner(settings)


class General:
    prompt = ''

    def __init__(
        self, *, job_key: str, memory: BaseMemory, settings: Settings,
        roles = load_roles, runner = load_runner
    ) -> None:
        self.job_key = job_key
        self.memory = memory
        self.settings = settings
        self.completed = []
        self.action_plan = []
        self.roles = roles(settings)
        self.runner = runner(settings)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.job_key})"

    def start_job(self) -> None:
        print(f"Starting job {self.job_key}")
        # Load the job configuration and history
        self.memory.load(self.job_key)
        if not self.memory.history:
            print("No history found")
        # Validate the action plan and perform the actions
        while True:
            try:
                self.update_action_plan()
                self.run_next_action()
            except JobFinished:
                break
        # Mark the job as completed
        print(f"Job {self.job_key} completed")

    def run_next_action(self) -> None:
        if self.action_plan:
            action_item = self.action_plan.pop(0)
            print(f"Try running action: {action_item} with {self.runner}")
            action, result = self.runner(action_item)
            print(f"Action result: {result}")
            if result and not self.action_plan:
                self.plan_next_actions(f"Output of '{action}()': {result}")
        else:
            raise JobFinished()

    def update_action_plan(self) -> None:
        assert self.prompt
        if self.memory.history.is_empty:
            self.plan_next_actions(self.prompt)
        print(f"Action plan: {self.action_plan}")

    def plan_next_actions(self, instruction: str) -> None:
        if not self.memory.history.is_empty:
            print(f"Planning more actions: {instruction}")
        else:
            print(f"Planning initial actions: {instruction}")
        dialog = Dialog(self.settings, self.memory.history)
        instruction = f"{instruction}\n{FINISH_PROMPT}"
        dialog.send_message(instruction)
        reply = dialog.get_last_message()
        print(f"Parsing action plan: {reply}")
        self.action_plan = json_loads(reply)