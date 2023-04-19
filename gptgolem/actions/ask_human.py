def ask_human_action(text: str):
    try:
        result = input(text)
    except KeyboardInterrupt:
        return "Stop the job."
    return result
