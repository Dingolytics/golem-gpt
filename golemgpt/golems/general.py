from typing import List
from golemgpt.settings import Settings
from golemgpt.utils import console, genkey
from golemgpt.utils.memory.base import BaseMemory
from golemgpt.utils.dialog import Dialog
from golemgpt.runners import JustDoRunner
from golemgpt.utils.exceptions import (
    JobFinished, JobRejected, ParseActionsError
)
from .lexicon import GeneralLexicon

RETRY_PLAN_MAX_ATTEMPTS = 3


class General:
    lexicon_class = GeneralLexicon
    runner_class = JustDoRunner

    # TODO: Implement review_action_plan() ?
    # TODO: Spawn a new Golem to make parseable action plan from the reply ?

    def __init__(
        self, *, goals: List[str], job_key: str,
        memory: BaseMemory, settings: Settings
    ) -> None:
        self.action_plan = []
        self.job_key = job_key
        self.goals = goals
        self.memory = memory
        self.settings = settings
        self.lexicon = self.lexicon_class()
        self.runner = self.runner_class(settings)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.job_key})"

    def start_job(self) -> None:
        """Start the job."""
        console.info(f"Starting job: {self.job_key}")
        self.initialize()
        outcome = self.lexicon.goal_prompt(self.goals[-1])
        while True:
            try:
                if outcome:
                    self.plan_next_actions(outcome)
                outcome = self.run_next_action()
            except JobFinished:
                break
            except JobRejected:
                break
        console.info(f"Job completed: {self.job_key}")

    def initialize(self) -> None:
        """Initialize the job state from memory or from scratch."""
        console.debug(f"Syncing job state with memory: {self.job_key}")
        self.memory.load(self.job_key)

        if self.memory.is_history_empty:
            self.memory.goals = self.goals
            iniital_history = self.lexicon.initializer_history()
            for message in iniital_history:
                self.memory.messages.append(message)
        else:
            self.goals = self.memory.goals
            assert self.goals

        self.memory.save()

    def run_next_action(self) -> str:
        """Run the next action in the plan."""
        if not self.action_plan:
            raise JobFinished()
        action_item = self.action_plan.pop(0)
        action, result = self.runner(action_item, golem=self)
        if not result:
            return ''
        return self.lexicon.action_result_prompt(action, result)

    def plan_next_actions(self, prompt: str, attempt: int = 0) -> None:
        """Ask to update the plan based on the prompt."""
        console.message('user', prompt)
        # TODO: Trigger memory save inside dialog
        dialog = Dialog(self.settings, self.memory)
        dialog.send_message(prompt)
        reply = dialog.get_last_message()
        self.memory.save()
        console.message('golem-gpt', reply)
        try:
            self.action_plan = self.lexicon.parse_reply(reply)
        except ParseActionsError:
            self.retry_plan_next_actions(reply, attempt + 1)

    def retry_plan_next_actions(self, reply: str, attempt: int = 0) -> None:
        """Ask to retry the plan based on the reply."""
        # Finish if too many failed attempts:
        if attempt > RETRY_PLAN_MAX_ATTEMPTS:
            raise JobFinished()

        # Ask in a side dialog, if job is finished:
        question = self.lexicon.guess_finish_prompt(reply)
        if self.guess_yesno(question):
            raise JobFinished()

        # Try to plan again after remainder about the format:
        remainder = self.lexicon.remind_format_prompt()
        self.plan_next_actions(remainder, attempt + 1)

    # TODO: Extract side dialog to a separate class (1)
    def side_dialog(self, prompt: str) -> str:
        """Spawn a side dialog to interpret the mainline replies."""
        console.message('user', prompt)
        key = f'{self.job_key}.{genkey()}'
        memory = self.memory.spawn(key)
        dialog = Dialog(self.settings, memory)
        dialog.send_message(prompt, temperature=0)
        reply = dialog.get_last_message()
        memory.save()
        console.message('quick', reply)
        return reply

    # TODO: Extract side dialog to a separate class (2)
    def guess_yesno(self, question: str) -> bool:
        """Guess if the reply is a yes or no."""
        prompt = self.lexicon.guess_yesno_prompt(question)
        yesno = self.side_dialog(prompt)
        return yesno.lower().startswith('y')
