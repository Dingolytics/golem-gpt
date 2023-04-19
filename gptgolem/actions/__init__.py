from .ask_human import ask_human_action
from .get_datetime import get_datetime_action
from .finish_job import finish_job_action
from .finish_job import JobFinished
from .search_web import search_google_action

__all__ = [
    'ask_human_action',
    'get_datetime_action',
    'ALL_KNOWN_ACTIONS',
    'JobFinished',
]

ALL_KNOWN_ACTIONS = {
    'ask_human': ask_human_action,
    'get_datetime': get_datetime_action,
    'finish_job': finish_job_action,
    'search_google': search_google_action,
}
