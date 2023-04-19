def ask_human_action(text: str, **kwargs):
    try:
        result = input(f"{text}\n?> ")
    except KeyboardInterrupt:
        return "Stop the job."
    return result
