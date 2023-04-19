from json import loads as json_loads

from gptgolem.settings import Settings
from gptgolem.utils.memory.base import BaseMemory
from gptgolem.utils.chat.dialog import Dialog
from gptgolem.runners import JustDoRunner
from gptgolem.actions import JobFinished
from .defs import SYSTEM_PROMPT_FOR_GENERAL_DIRECTOR


def load_experts(settings: Settings) -> dict:
    return {}


def load_runners(settings: Settings) -> dict:
    return {
        'default': JustDoRunner(settings),
    }


def load_prompt(settings: Settings) -> str:
    return SYSTEM_PROMPT_FOR_GENERAL_DIRECTOR


class Director:
    def __init__(
        self, *, job_key: str, memory: BaseMemory, settings: Settings,
        experts = load_experts, runners = load_runners, prompt = load_prompt,
    ) -> None:
        self.job_key = job_key
        self.memory = memory
        self.settings = settings
        self.completed = []
        self.action_plan = []
        self.experts = experts(settings)
        self.runners = runners(settings)
        self.prompt = prompt(settings).strip()

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
            action = self.action_plan.pop(0)
            for runner_type, runner in self.runners.items():
                print(f"Try running action: {action} with {runner_type}")
                result = runner(action)
                print(f"Action result: {result}")
                if result:
                    break
            if result and not self.action_plan:
                self.plan_next_actions(result)
        else:
            raise JobFinished()

    def update_action_plan(self) -> None:
        if self.memory.history.is_empty:
            self.plan_next_actions(self.prompt)
        print(f"Action plan: {self.action_plan}")

    def plan_next_actions(self, instruction: str) -> None:
        if not self.memory.history.is_empty:
            print(f"Planning more actions: {instruction}")
        else:
            print("Planning initial actions.")
        dialog = Dialog(self.settings, self.memory.history)
        instruction = f"{instruction}\n If job is finished, say 'finish_job'."
        dialog.send_message(instruction)
        reply = dialog.get_last_message()
        print(f"Parsing action plan: {reply}")
        self.action_plan = json_loads(reply)
