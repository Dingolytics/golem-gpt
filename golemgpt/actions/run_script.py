from subprocess import PIPE, Popen
from golemgpt.utils import workpath


def run_script_action(name: str, **kwargs) -> str:
    """Run a script and return its output."""
    path = workpath(name)

    if not path.exists():
        return (
            f"Script {name} does not exist, please write if first. "
            "Use a proper extension like .sh or .py for saved file."
        )

    if name.endswith('.py'):
        process = Popen(['python', name], stdout=PIPE, stderr=PIPE)
    elif name.endswith('.sh'):
        process = Popen(['sh', name], stdout=PIPE, stderr=PIPE)
    else:
        return f"Rejected: script {name} is not a Bash or Python script."

    output, error = process.communicate()
    is_ok = (process.returncode == 0)

    if isinstance(output, bytes):
        output = output.decode("utf-8")

    if isinstance(error, bytes):
        error = error.decode("utf-8")

    return (
        f"Script {name} executed successfully. Output:\n{output}"
        if is_ok else
        f"Script {name} failed. Error:\n{error}"
    )
