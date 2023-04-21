from golemgpt.utils.exceptions import JobFinished


def finish_job_action(**kwargs):
    raise JobFinished()
