from golemgpt.actions import ALL_KNOWN_ACTIONS
from golemgpt.codex import BaseCodex
from golemgpt.lexicon import BaseLexicon
from golemgpt.codex import ReasonableCodex
from golemgpt.runners import JustDoRunner
from golemgpt.settings import Settings
from golemgpt.memory import BaseMemory
from golemgpt.utils import console, genkey
from golemgpt.cognitron.base import BaseCognitron

# from golemgpt.cognitron.openai import OpenAITextCognitron
from golemgpt.cognitron.openai import OpenAIToolsCognitron
from golemgpt.utils.exceptions import (
    GolemError,
    AlignAcionsError,
    JobFinished,
    JobRejected,
    ParseActionsError,
    PathRejected,
)

DEFAULT_NAME = "Golem-GPT"

DEFAULT_RETRY_PLAN_ATTEMPTS = 3


class GeneralGolem:
    cognitron_class = OpenAIToolsCognitron
    codex_class = ReasonableCodex
    runner_class = JustDoRunner

    def __init__(
        self,
        *,
        name=DEFAULT_NAME,
        goals: list[str],
        job_key: str,
        memory: BaseMemory,
        settings: Settings,
    ) -> None:
        self.name = name
        self.action_plan = []
        self.job_key = job_key
        self.goals = goals
        self.memory = memory
        self.settings = settings
        self.runner = self.runner_class(settings)
        self.core = self.cognitron_class(
            settings=self.settings,
            memory=memory,
            actions=ALL_KNOWN_ACTIONS,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.job_key})"

    @property
    def lexicon(self) -> BaseLexicon:
        return self.core.lexicon

    def start_job(self) -> None:
        """Start the job."""
        goals_text = "\n".join(self.goals)
        console.info(f"Starting job: {self.job_key}")
        console.info(f"Goals:\n{goals_text}")

        self.initialize()
        outcome = self.lexicon.goal_prompt(self.goals[-1])
        while True:
            try:
                if outcome:
                    action_plan = self.core.plan_actions(outcome)
                    if self.codex().align_actions(action_plan):
                        self.action_plan = action_plan
                outcome = self.run_action()
            except JobFinished:
                break
            except JobRejected:
                break
            except PathRejected:
                break
            except AlignAcionsError as exc:
                # TODO: Implement a retry plan mechanism after misalignment
                console.info(f"Actions rejected: {exc}")
                break
            except GolemError as exc:
                outcome = str(exc)

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

    def spawn_cognitron(self, **options) -> BaseCognitron:
        """Return a Cognitron instance."""
        assert self.settings, "Error: settings must be initialized first."
        assert self.memory, "Error: memory must be initialized first."
        key = f"{self.job_key}.{genkey()}"
        memory = self.memory.spawn(key)
        return self.cognitron_class(
            settings=self.settings,
            memory=memory,
            actions=ALL_KNOWN_ACTIONS,
            **options,
        )

    def codex(self, **options) -> BaseCodex:
        """Return a Codex instance."""
        cognitron = self.spawn_cognitron(name="Codex", **options)
        return self.codex_class(cognitron)

    def run_action(self) -> str:
        """Run the next action in the plan."""
        if not self.action_plan:
            raise JobFinished()
        action_item = self.action_plan.pop(0)
        action, result = self.runner(action_item, golem=self)
        if not result:
            return ""
        return self.lexicon.action_result_prompt(action, result)

    def plan_actions(self, prompt: str, attempt: int = 0) -> None:
        """Ask to update the plan based on the prompt."""
        console.message(self.name, prompt)
        reply = self.core.communicate(prompt)
        try:
            self.action_plan = self.core.plan_actions(prompt)
        except ParseActionsError:
            self.try_restore_plan(reply, attempt + 1)

    def align_actions(self, prompt: str) -> list[str]:
        """Align the action plan with the codex."""
        return self.codex().align_actions(self.action_plan)

    def try_restore_plan(self, reply: str, attempt: int = 0) -> None:
        """Try restore the plan after malformed reply."""
        # Finish if too many failed attempts:
        if attempt > DEFAULT_RETRY_PLAN_ATTEMPTS:
            raise JobFinished()

        # Ask in a helper dialog, if job is finished:
        question = self.lexicon.guess_finish_prompt(reply)
        if self.helper_yesno(question):
            raise JobFinished()

        # Try to plan again after remainder about the format:
        remainder = self.lexicon.remind_format_prompt()
        self.plan_actions(remainder, attempt + 1)

    def helper_yesno(self, question: str) -> bool:
        """Guess if the reply is a yes or no."""
        prompt = self.lexicon.yesno_prompt(question)
        cognitron = self.spawn_cognitron(name="Helper")
        return cognitron.ask_yesno(prompt)
