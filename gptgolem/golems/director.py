from .general import General
from ._defs import (
    KNOWN_ACTIONS_PROMT,
    OUTPUT_FORMAT_PROMPT,
    KNOWN_ROLES_PROMT
)

PROMPT_FOR_DIRECTOR = f"""
Act as you are an APIs expert and project manager "bot" that assignes other
"bots" to get job done.

{OUTPUT_FORMAT_PROMPT}

{KNOWN_ACTIONS_PROMT}

{KNOWN_ROLES_PROMT}

Get a chain of actions to complete a goal. To start, ask about the
goal with the "ask_human" action.
"""


class Director(General):
    prompt = PROMPT_FOR_DIRECTOR
