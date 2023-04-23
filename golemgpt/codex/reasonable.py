from golemgpt.utils import console
from golemgpt.utils.exceptions import AlignAcionsError
from .base import BaseCodex, BaseCodexLexicon


class ReasonableCodexLexicon(BaseCodexLexicon):
    def align_actions_prompt(self, action_plan: list) -> str:
        question = f"In this action plan unharmful? Action:\n{action_plan}"
        return f"Answer just 'yes' or 'no'. {question}"


class ReasonableCodex(BaseCodex):
    name = 'reasonable-codex'
    lexicon = ReasonableCodexLexicon()

    def align_actions(self, action_plan: list) -> str:
        prompt = self.lexicon.align_actions_prompt(action_plan)
        console.message(self.name, prompt)
        if self.cognitron.ask_yesno(prompt):
            return True
        console.message(self.name, prompt)
        raise AlignAcionsError()
