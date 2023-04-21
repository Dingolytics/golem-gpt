from golemgpt.utils import console
from golemgpt.utils.exceptions import JobRejected


def reject_job_action(**kwargs) -> str:
    """Reject a job."""
    console.debug(f"Rejecting job: {kwargs}")
    raise JobRejected()
