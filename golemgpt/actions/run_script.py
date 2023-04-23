import subprocess
from golemgpt.utils import workpath


def run_script_action(name: str, **kwargs) -> str:
    """Run a script and return its output."""
    path = workpath(name)

    if not path.exists():
        return f"Script {name} does not exist, can you create it?"

    if name.endswith('.py'):
        process = subprocess.Popen(['python', name])
    elif name.endswith('.sh'):
        process = subprocess.Popen(['sh', name])
    else:
        return f"Rejected: script {name} is not a Bash or Python script."

    process.wait()
    is_ok = (process.returncode == 0)

    return (
        f"Script {name} executed successfully."
        if is_ok else
        f"Script {name} failed."
    )
