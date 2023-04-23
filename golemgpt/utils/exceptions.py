from json import JSONDecodeError


class GolemError(Exception):
    """Base class for all Golem errors."""


class JobFinished(GolemError):
    """Exception to be raised when the job is finished."""


class JobRejected(GolemError):
    """Exception to be raised when the job is rejected."""


class PathRejected(GolemError, ValueError):
    """Raised when a requested path is rejected."""
    def __init__(self, path: str, *args):
        self.path = path
        super().__init__(*args)


class UnknownAction(GolemError, RuntimeError):
    """Raised when unknown action is requested."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Unknown action: {name}.")


class AlignAcionsError(GolemError):
    """Exception to be raised when the action plan is rejected."""


class ParseActionsError(GolemError, JSONDecodeError):
    """Raised when actions plan cannot be parsed."""

    def __init__(self, msg: str, doc: str, pos: int = 0):
        super().__init__(msg, doc, pos)
