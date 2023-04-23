from golemgpt.utils import workpath
from .write_file import write_file_action

MAX_RAW_SIZE = 32768


def summarize_file_action(
    filename: str, hint: str, out_filename: str, **kwargs
) -> str:
    # TODO: Better way to import for type checking
    from golemgpt.golems import GeneralGolem  # noqa
    golem = kwargs['golem']  # type: GeneralGolem
    # TODO: Split file into chunks for summarization
    path = workpath(filename, check_exists=True)
    with path.open("r") as file:
        content = file.read()
    content = content[:MAX_RAW_SIZE]
    cognitron = golem.cognitron(spawn=True)
    prompt = f"Summarize the text, use the hint '{hint}':\n\n{content}"
    reply = cognitron.communicate(prompt)
    return write_file_action(out_filename, reply)
