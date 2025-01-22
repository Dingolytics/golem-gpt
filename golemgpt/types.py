from typing import Any, Callable

# Action definition as a function that accepts arbitrary
# kwargs and returns a string.
ActionFn = Callable[..., str]

# Action item to be executed by the runner:
# - action name as a key
# - arguments as a value
ActionItem = dict[str, dict[str, Any]]

# Action plan to be executed by the runner: list of action items.
ActionPlan = list[ActionItem]
