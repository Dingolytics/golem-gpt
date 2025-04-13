from golemgpt.codex import BaseCodex
from golemgpt.handlers.base import BaseHandler
from golemgpt.runners.base import BaseRunner
from golemgpt.settings import Settings
from golemgpt.memory import BaseMemory
from golemgpt.utils import console, genkey
from golemgpt.cognitron.base import BaseCognitron
from golemgpt.types import ActionFn, ActionItem

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

    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        goals: list[str],
        job_key: str,
        memory: BaseMemory,
        settings: Settings,
        actions: dict[str, ActionFn | BaseHandler],
    ) -> None:
        self.name = name
        self.actions = actions
        self.plan: list[ActionItem] = []
        self.job_key = job_key
        self.goals = goals
        self.memory = memory
        self.settings = settings
        self.codex_class = settings.CODEX_CLASS
        self.runner_class = settings.RUNNER_CLASS
        self.core = self.cognitron(
            actions=actions,
            verbosity=self.settings.VERBOSITY_MAIN,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.job_key})"

    def start_job(self) -> None:
        """Start the job."""
        goals_text = "\n".join(self.goals)
        console.info(f"Starting job: {self.job_key}")
        console.info(f"Goals:\n{goals_text}")

        self.initialize()

        # Start loop with mocking output from goals.
        output = self.core.lexicon.goal_prompt(self.goals[-1])

        while True:
            try:
                if output:
                    proposed_plan = self.plan_actions(output)
                    self.align_actions(proposed_plan)
                    self.plan = proposed_plan
                output = self.run_action()
            except JobFinished as exc:
                console.info(f"{exc} {self.job_key}")
                break
            except JobRejected as exc:
                console.info(f"{exc} {self.job_key}")
                break
            except PathRejected as exc:
                console.info(f"{exc} {self.job_key}")
                break
            except AlignAcionsError as exc:
                console.info(f"{exc} {self.job_key}")
                break
            except GolemError as exc:
                output = str(exc)

    def initialize(self) -> None:
        """Initialize the job state from memory or from scratch."""
        console.debug(f"Syncing job state with memory: {self.job_key}")
        self.memory.load(self.job_key)

        if self.memory.is_history_empty:
            self.memory.goals = self.goals
            iniital_history = self.core.lexicon.initializer_history()
            for message in iniital_history:
                self.memory.messages.append(message)
        else:
            self.goals = self.memory.goals
            assert self.goals

        self.memory.save()

    def cognitron(
        self, actions: dict[str, ActionFn | BaseHandler], **options
    ) -> BaseCognitron:
        """Return a new Cognitron instance."""
        assert self.settings, "Error: settings must be initialized first."
        assert self.memory, "Error: memory must be initialized first."
        key = f"{self.job_key}/{genkey()}"
        memory = self.memory.spawn(key)
        return self.cognitron_class(
            settings=self.settings,
            memory=memory,
            actions=actions,
            **options,
        )

    def codex(self, **options) -> BaseCodex:
        """Return a new Codex instance."""
        assert self.settings, "Error: settings must be initialized first."
        assert self.memory, "Error: memory must be initialized first."
        key = f"{self.job_key}/{genkey()}"
        return self.codex_class(
            settings=self.settings,
            memory=self.memory.spawn(key)
        )  # fmt: skip

    def runner(self) -> BaseRunner:
        """Return a new Runner instance."""
        return self.runner_class(self)

    def run_action(self) -> str:
        """Run the next action in the plan."""
        if not self.plan:
            raise JobFinished()
        runner = self.runner()
        action_item = self.plan.pop(0)
        action, result = runner(action_item)
        if not result:
            return ""
        return self.core.lexicon.action_result_prompt(action, result)

    def plan_actions(self, prompt: str, attempt: int = 0) -> list[dict]:
        """Generate an action plan based on the prompt."""
        try:
            action_plan = self.core.plan_actions(prompt)
        except ParseActionsError:
            # TODO: Ingest format reminder message to the memory and retry,
            # check `lexicon.remind_format_prompt()`.
            raise
        return action_plan

    def align_actions(self, action_plan: list[dict]) -> None:
        """Align the action plan with the codex."""
        self.codex().align_actions(action_plan)
