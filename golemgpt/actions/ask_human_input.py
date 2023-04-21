from golemgpt.utils.exceptions import JobFinished


def ask_human_input_action(query: str, **kwargs):
    try:
        result = input(f"{query}\n?> ")
    except KeyboardInterrupt:
        raise JobFinished()
    return f"{query}\nAnswer is: {result}"
