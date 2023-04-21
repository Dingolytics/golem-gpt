import os
import platform


def get_os_details_action(**kwargs) -> str:
    return {
        'os': os.name,
        'platform': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'architecture': platform.machine(),
    }
