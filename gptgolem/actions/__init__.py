from .human_input import human_input_action
from .get_datetime import get_datetime_action
from .finish_job import finish_job_action
from .finish_job import JobFinished
from .search_web import ask_google_action

__all__ = [
    'human_input_action',
    'ask_google_action',
    'get_datetime_action',
    'ALL_KNOWN_ACTIONS',
    'JobFinished',
]

ALL_KNOWN_ACTIONS = {
    'get_datetime': get_datetime_action,
    'finish_job': finish_job_action,
    'human_input': human_input_action,
    'ask_google': ask_google_action,
}


class UnknownAction(RuntimeError):
    """Raised when unknown action is requested."""

    def __init__(self, action_name: str):
        super().__init__(f"Unknown action: {action_name}")
