from re import compile as re_compile, DOTALL
from json import loads as json_loads, JSONDecodeError
from typing import List
from golemgpt.settings import Settings
from golemgpt.utils import console, genkey
from golemgpt.utils.memory.base import BaseMemory
from golemgpt.utils.dialog import Dialog
from golemgpt.runners import JustDoRunner
from golemgpt.utils.exceptions import JobFinished, JobRejected
from .lexicon import GeneralLexicon


class General:
    lexicon_class = GeneralLexicon
    runner_class = JustDoRunner

    # Not-a-JSON naive preambule regex:
    naive_preambule_re = re_compile(r'([^\[\{]*)', DOTALL)

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
        console.info(f"Starting job: {self.job_key}")
        self.initialize()
        outcome = self.get_goal_prompt()
        while True:
            try:
                if outcome:
                    self.plan_next_actions(outcome)
                outcome = self.run_next_action()
            except JobFinished:
                break
            except JobRejected:
                break
        console.info(f"Job {self.job_key} completed")

    def run_next_action(self) -> str:
        if self.action_plan:
            action_item = self.action_plan.pop(0)
            action, result = self.runner(action_item, golem=self)
            if not result:
                return ''
            return f'Completed "{action}" with result:\n{result}'
        else:
            raise JobFinished()

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

    def initialize(self) -> None:
        console.debug(f"Syncing job state with memory: {self.job_key}")
        self.memory.load(self.job_key)

        if self.memory.is_history_empty:
            self.memory.goals = self.goals
            iniital_history = self.lexicon.initializer_history()
            for message in iniital_history:
                self.memory.messages.append(message)
        else:
            self.goals = self.memory.goals
            assert self.goals, "Goals not provided, and not found in memory"

        self.memory.save()

    def get_goal_prompt(self) -> List[str]:
        return f"The goal is: {self.goals[-1]} Then finish the job."

    def parse_reply(self, reply: str) -> List[dict]:
        """Parse the reply into an action plan."""
        console.debug(f"Parse plan:\n{reply}\n")
        preambule = self.naive_preambule_re.search(reply)
        if preambule:
            preambule = preambule.group()
            reply = reply[len(preambule):]
            console.debug(f"Parse plan (trunc.):\n{reply}\n")
        reply = reply.strip()
        if reply:
            parsed = json_loads(reply)
            if isinstance(parsed, dict):
                parsed = [parsed]
            self.action_plan = parsed
        else:
            raise JSONDecodeError("JSON not found", reply, 0)

    def plan_next_actions(self, prompt: str, attempt: int = 0) -> None:
        """Ask to update the plan based on the prompt."""
        dialog = Dialog(self.settings, self.memory)
        console.message('user', prompt)
        # role = 'system' if self.memory.is_history_empty else 'user'
        dialog.send_message(prompt)
        reply = dialog.get_last_message()
        self.memory.save()
        console.message('golem-gpt', reply)
        try:
            self.parse_reply(reply)
        except JSONDecodeError:
            preambule = self.naive_preambule_re.search(reply)
            if preambule:
                reply = preambule.group()
            question = (
                "Does the following mean current job is finished"
                f" (optional ask to start a new one)?\n\n{reply}"
            )
            if self.guess_yesno(question):
                raise JobFinished()
            else:
                retry = self.lexicon.wrong_format_prompt()
                self.plan_next_actions(retry, attempt + 1)
