from golemgpt.actions.ask_human_input import ask_human_input_action
from golemgpt.actions.finish_job import finish_job_action
from golemgpt.actions.get_local_date import get_local_date_action
from golemgpt.actions.get_os_details import get_os_details_action
from golemgpt.actions.http_download import http_download_action
from golemgpt.actions.read_file import read_file_action
from golemgpt.actions.reject_job import reject_job_action
from golemgpt.actions.run_script import run_script_action
from golemgpt.actions.search_text_via_brave import search_text_via_brave_action
from golemgpt.actions.summarize_file import summarize_file_action
from golemgpt.actions.write_file import write_file_action
from golemgpt.handlers.http_download import HttpDownloadHandler

__all__ = [
    "GeneralActions",
]


def reply_yes_or_no(answer: str) -> bool:
    return answer.lower().startswith("yes")


class GeneralActions:
    """General actions set to fulfil goals."""

    @classmethod
    def get_actions(cls):
        return {
            "http_download": HttpDownloadHandler(),
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
