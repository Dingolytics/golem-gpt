from .ask_human_input import ask_human_input_action
from .get_datetime import get_datetime_action
from .finish_job import finish_job_action
from .finish_job import JobFinished
from .ask_google import ask_google_action
from .read_file import read_file_action
from .write_file import write_file_action
from .http_request import http_request_action
from .create_python_script import create_python_script_action
from .create_shell_script import create_shell_script_action
from .run_script import run_script_action
from .delegate_job import delegate_job_action
from .reject_job import reject_job_action
from .reject_job import JobRejected
from .explain import explain_action

__all__ = [
    # Get more information actions
    'ask_human_input_action',
    'ask_google_action',

    # Get environment actions
    'get_datetime_action',

    # Files actions
    'read_file_action',
    'write_file_action',

    # HTTP actions
    'http_request_action',

    # Scripts actions
    'create_python_script_action',
    'create_shell_script_action',
    'run_script_action',
    
    # Job flow actions
    'delegate_job_action',
    'finish_job_action',
    'reject_job_action',
    'JobFinished',
    'JobRejected',

    # Debug actions
    'explain_action',

    'ALL_KNOWN_ACTIONS',
]

ALL_KNOWN_ACTIONS = {
    'ask_human_input': ask_human_input_action,
    'ask_google': ask_google_action,
    #
    'http_request': http_request_action,
    #
    'read_file': read_file_action,
    'write_file': write_file_action,
    #
    'get_datetime': get_datetime_action,
    #
    'create_python_script': create_python_script_action,
    'create_shell_script': create_shell_script_action,
    'run_script': run_script_action,
    #
    'delegate_job': delegate_job_action,
    'reject_job': reject_job_action,
    'finish_job': finish_job_action,
    #
    'explain': explain_action,
}


class UnknownAction(RuntimeError):
    """Raised when unknown action is requested."""

    def __init__(self, action_name: str):
        super().__init__(f"Unknown action: {action_name}")
