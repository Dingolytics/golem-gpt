from .ask_human_input import ask_human_input_action
from .finish_job import finish_job_action
from .get_local_date import get_local_date_action
from .get_os_details import get_os_details_action
from .http_download import http_download_action
from .read_file import read_file_action
from .reject_job import reject_job_action
from .run_script import run_script_action
from .search_text_via_brave import search_text_via_brave_action
from .summarize_file import summarize_file_action
from .write_file import write_file_action

__all__ = [
    "GENERAL_ACTIONS",
]


def reply_yes_or_no(answer: str) -> bool:
    return answer.lower().startswith("yes")


GENERAL_ACTIONS = {
    "http_download": http_download_action,
    #
    "read_file": read_file_action,
    "summarize_file": summarize_file_action,
    "write_file": write_file_action,
    #
    "get_local_date": get_local_date_action,
    "get_os_details": get_os_details_action,
    #
    "run_script": run_script_action,
    #
    # "explain": explain_action,
    #
    "ask_human_input": ask_human_input_action,
    # "delegate_job": delegate_job_action,
    "reject_job": reject_job_action,
    "finish_job": finish_job_action,
    #
    # "search_images_online": search_images_via_bing_action,
    "search_text_via_brave": search_text_via_brave_action,
}


CODEX_ACTIONS = {"reply_yes_or_no": reply_yes_or_no}
