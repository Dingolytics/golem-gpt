def ask_human_input_action(query: str, **kwargs):
    try:
        result = input(f"{query}\n?> ")
    except KeyboardInterrupt:
        return "Stop the job."
    return result
