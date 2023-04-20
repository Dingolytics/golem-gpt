from datetime import datetime


def get_datetime_action(**kwargs) -> str:
    return f"{datetime.utcnow()}+00:00"
