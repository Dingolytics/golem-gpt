from golemgpt.utils import console
from golemgpt.utils.exceptions import AlignAcionsError
from .base import BaseCodex


class ReasonableCodex(BaseCodex):
    check_actions_depth = 3
    name = "reasonable-codex"

    def is_job_finished(self, actions: list[dict]) -> bool:
        if len(actions) == 1:
            return next(iter(actions[0].keys())) == "finish_job"
        return False

    def align_actions_prompt(self, actions: list[dict]) -> tuple[str, bool]:
        actions_summary = ", ".join(
            map(lambda a: next(iter(a.keys())), actions)
        )
        is_unsafe_question = (
            "Is the following action plan harmful? "
            "NOTES: Consider asking user input as safe. "
            "Be reasonable but not paranoid. "
            f"ACTIONS: {actions_summary}"
        )
        return self.cognitron.lexicon.yesno_prompt(is_unsafe_question), False

    def align_actions(self, actions: list[dict]) -> bool:
        """Check if the actions are reasonably safe to perform."""

        if self.is_job_finished(actions):
            return True

        check_actions = actions[: self.check_actions_depth]
        prompt, answer_expected = self.align_actions_prompt(check_actions)
        console.message(self.name, prompt)
        answer_real = self.cognitron.ask_yesno(prompt)
        if answer_expected == answer_real:
            return True

        raise AlignAcionsError(prompt)
