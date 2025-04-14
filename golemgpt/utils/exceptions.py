from json import JSONDecodeError


class WorkflowError(Exception):
    """Base class for all workflow errors."""


class JobFinished(WorkflowError):
    """Exception to be raised when the job is finished."""


class JobRejected(WorkflowError):
    """Exception to be raised when the job is rejected."""


class PathRejected(WorkflowError, ValueError):
    """Raised when a requested path is rejected."""

    def __init__(self, path: str, *args):
        self.path = path
        super().__init__(*args)


class UnknownReplyFormat(WorkflowError, RuntimeError):
    """Raised when reply format is unknown."""


class UnknownAction(WorkflowError, RuntimeError):
    """Raised when unknown action is requested."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Unknown action: {name}.")


class AlignAcionsError(WorkflowError):
    """Exception to be raised when the action plan is rejected."""


class ParseActionsError(WorkflowError, JSONDecodeError):
    """Raised when actions plan cannot be parsed."""

    def __init__(self, msg: str, doc: str, pos: int = 0):
        super().__init__(msg, doc, pos)
