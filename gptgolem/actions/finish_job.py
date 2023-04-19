class JobFinished(Exception):
    """Exception to be raised when the job is finished."""
    pass


def finish_job_action(**kwargs):
    raise JobFinished()
