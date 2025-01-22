from datetime import UTC, datetime


def get_local_date_action(**kwargs) -> str:
    """Get the current date and time in UTC timezone."""
    return datetime.now(UTC).isoformat()


if __name__ == "__main__":
    print(get_local_date_action())
