from golemgpt.cognitron import BaseCognitron


class BaseCodexLexicon:
    def align_actions(self, action_plan: list) -> str:
        raise NotImplementedError()


class BaseCodex:
    def __init__(self, cognitron: BaseCognitron):
        self.cognitron = cognitron

    def align_actions(self, action_plan: list) -> str:
        raise NotImplementedError()
