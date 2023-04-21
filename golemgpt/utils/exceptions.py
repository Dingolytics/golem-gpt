from json import JSONDecodeError


class JobFinished(Exception):
    """Exception to be raised when the job is finished."""


class JobRejected(Exception):
    """Exception to be raised when the job is rejected."""


class PathRejected(ValueError):
    """Raised when a requested path is rejected."""
    def __init__(self, path: str, *args):
        self.path = path
        super().__init__(*args)


class UnknownAction(RuntimeError):
    """Raised when unknown action is requested."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Unknown action: {name}.")


class ParseActionsError(JSONDecodeError):
    """Raised when actions plan cannot be parsed."""

    def __init__(self, msg: str, doc: str, pos: int = 0):
        super().__init__(msg, doc, pos)