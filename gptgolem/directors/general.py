from json import loads as json_loads

from gptgolem.settings import Settings
from gptgolem.utils.memory.base import BaseMemory
from gptgolem.utils.chat.dialog import Dialog
from gptgolem.runners import JustDoerRunner
from gptgolem.actions import (
    ask_human_action
)
from .defs import SYSTEM_PROMPT_FOR_GENERAL_DIRECTOR


def load_experts(settings: Settings) -> dict:
    return {}


def load_runners(settings: Settings) -> dict:
    return {
        'default': JustDoerRunner(settings),
    }


def load_prompt(settings: Settings) -> str:
    return SYSTEM_PROMPT_FOR_GENERAL_DIRECTOR


def load_actions(settings: Settings) -> dict:
    return {
        'ask_human': ask_human_action,
    }


class Director:
    def __init__(
        self, *, job_key: str, memory: BaseMemory, settings: Settings,
        actions = load_actions, experts = load_experts, runners = load_runners,
        prompt = load_prompt,
    ) -> None:
        self.job_key = job_key
        self.memory = memory
        self.settings = settings
        self.completed = []
        self.action_plan = []
        self.actions = actions(settings)
        self.experts = experts(settings)
        self.runners = runners(settings)
        self.prompt = prompt(settings).strip()

    def start_job(self):
        print(f"Starting job {self.job_key}")
        # Load the job configuration and history
        self.memory.load(self.job_key)
        if not self.memory.history:
            print("No history found")
        # Validate the action plan and perform the actions
        while True:
            self.validate_action_plan()
            if not self.action_plan:
                break
            action = self.action_plan.pop(0)
            for runner_type, runner in self.runners.items():
                print(f"Try running action: {action} with {runner_type}")
                result = runner(action)
                print(f"Action result: {result}")
        # Mark the job as completed
        print(f"Job {self.job_key} completed")

    def bootstrap_action_plan(self) -> None:
        dialog = Dialog(self.settings, self.memory.history)
        dialog.send_message(self.prompt)
        reply = dialog.get_last_message()
        self.action_plan = self.parse_action_plan(reply)

    def parse_action_plan(self, reply: str) -> list:
        return json_loads(reply)

    def validate_action_plan(self):
        if self.memory.history.is_empty:
            self.bootstrap_action_plan()
        print(f"Validating action plan: {self.action_plan}")
