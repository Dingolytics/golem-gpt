from golemgpt.utils import console
from golemgpt.utils.exceptions import AlignAcionsError
from .base import BaseCodex


class ReasonableCodex(BaseCodex):
    check_actions_depth = 3
    name = 'reasonable-codex'

    def align_actions_prompt(self, action_plan: list) -> str:
        question = f"In this action plan unharmful? Actions: {action_plan}"
        lexicon = self.cognitron.lexicon
        return lexicon.yesno_prompt(question)

    def align_actions(self, action_plan: list) -> bool:
        check_actions = action_plan[:self.check_actions_depth]
        prompt = self.align_actions_prompt(check_actions)
        brief = self.align_actions_prompt(['...'])
        console.message(self.name, brief)
        if self.cognitron.ask_yesno(prompt):
            return True
        raise AlignAcionsError(prompt)
