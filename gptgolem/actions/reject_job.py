class JobRejected(Exception):
    """Exception to be raised when the job is rejected."""
    pass


def reject_job_action(**kwargs) -> str:
    """Reject a job."""
    print(f"Rejecting job: {kwargs}")
    raise JobRejected()
