from golemgpt.actions import CODEX_ACTIONS
from golemgpt.settings import Verbosity
from golemgpt.utils import console
from golemgpt.utils.exceptions import AlignAcionsError
from golemgpt.cognitron.openai import OpenAIToolsCognitron
from .base import BaseCodex


class ReasonableCodex(BaseCodex):
    _cognitron: OpenAIToolsCognitron | None = None

    _name: str = "Reasonable-Codex"

    check_actions_depth = 3

    prescription_prompt = (
        "Is the following action plan harmful? "
        "NOTES: Consider asking user input as safe. "
        "Consider running known scripts as safe if aligned with goals. "
        "Be reasonable but not paranoid. "
    )

    message_ok = "Action looks OK."

    @property
    def cognitron(self) -> OpenAIToolsCognitron:
        if not self._cognitron:
            return OpenAIToolsCognitron(
                settings=self.settings,
                memory=self.memory,
                actions=CODEX_ACTIONS,
                name=self.name,
                verbosity=self.settings.VERBOSITY_CODEX,
            )
        return self._cognitron

    @property
    def name(self) -> str:
        return self._name

    def is_job_finished(self, actions: list[dict]) -> bool:
        if len(actions) == 1:
            return next(iter(actions[0].keys())) == "finish_job"
        return False

    def align_actions_prompt(self, actions: list[dict]) -> tuple[str, bool]:
        actions_summary = ""
        for item in actions:
            name = next(iter(item.keys()))
            actions_summary += f"\n{name}:\narguments = {item[name]}\n"
        prompt = f"{self.prescription_prompt}"
        prompt += f"ACTIONS: {actions_summary}"
        return self.cognitron.lexicon.yesno_prompt(prompt), False

    def align_actions(self, actions: list[dict]) -> bool:
        """Check if the actions are reasonably safe to perform."""

        if self.is_job_finished(actions):
            return True

        check_actions = actions[: self.check_actions_depth]
        prompt, answer_expected = self.align_actions_prompt(check_actions)

        if self.cognitron.verbosity >= Verbosity.VERBOSE:
            console.message(self.name, prompt, tags=["prompt"])

        answer_real = self.cognitron.ask_yesno(prompt)
        if answer_expected == answer_real:
            console.message(self.name, self.message_ok, tags=["align"])
            return True

        raise AlignAcionsError(prompt)
