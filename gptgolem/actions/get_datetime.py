from datetime import datetime


def get_datetime_action(**kwargs) -> str:
    return f"Current date and time is {datetime.utcnow()} UTC"
