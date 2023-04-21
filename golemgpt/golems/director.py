from .general import General
from ._defs import (
    KNOWN_ACTIONS_PROMT,
    OUTPUT_FORMAT_PROMPT,
    KNOWN_ROLES_PROMT,
    FINISH_CHECK_PROMPT,
)

# Use the real APIs, trigger search actions to get extra information when needed.
# Autonomous bots are preferred. Ask for all prerequisite on start.
# For example, travel dates, preferences, or API credentials.

# Act as a Solutions architect and expert in APIs to create pipeline for bots
# to achieve the specified goals. Autonomous bots are preferred.

PROMPT_FOR_DIRECTOR = f"""
Act as a Solutions architect and expert in APIs. Write a pseudo-code
defining a list of actions to execute, so bots could understand that.

You provide a list of actions, bots will execute them and you
will get results.

Bypass already executed actions, use results provided.

{OUTPUT_FORMAT_PROMPT}

{KNOWN_ACTIONS_PROMT}

{KNOWN_ROLES_PROMT}

{FINISH_CHECK_PROMPT}
""".strip()


class Director(General):
    prompt = PROMPT_FOR_DIRECTOR
