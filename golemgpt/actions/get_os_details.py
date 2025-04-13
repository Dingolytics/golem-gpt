import json
import os
import platform


def get_os_details_action(**kwargs) -> str:
    """Get the details of the host operating system."""
    return json.dumps(
        {
            "os": os.name,
            "platform": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
        }
    )


if __name__ == "__main__":
    print(get_os_details_action())
