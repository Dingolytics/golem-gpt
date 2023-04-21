from datetime import datetime


def get_local_date_action(**kwargs) -> str:
    return f"{datetime.utcnow()}+00:00"
