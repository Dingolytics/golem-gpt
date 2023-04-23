from golemgpt.utils import console
from golemgpt.utils.exceptions import AlignAcionsError
from .base import BaseCodex, BaseCodexLexicon


class ReasonableCodexLexicon(BaseCodexLexicon):
    def align_actions_prompt(self, action_plan: list) -> str:
        question = f"In this action plan unharmful? Actions: {action_plan}"
        return f"Answer just 'yes' or 'no'. {question}"


class ReasonableCodex(BaseCodex):
    check_actions_depth = 3
    name = 'reasonable-codex'
    lexicon = ReasonableCodexLexicon()

    def align_actions(self, action_plan: list) -> str:
        check_actions = action_plan[:self.check_actions_depth]
        prompt = self.lexicon.align_actions_prompt(check_actions)
        brief = self.lexicon.align_actions_prompt('[...]')
        # console.debug(self.name, prompt)
        console.message(self.name, brief)
        if self.cognitron.ask_yesno(prompt):
            return True
        raise AlignAcionsError(prompt)
