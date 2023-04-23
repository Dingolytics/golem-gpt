from golemgpt.golems.general import GeneralGolem
from golemgpt.lexicon.general import GeneralLexicon

# Use the real APIs, trigger search actions to get extra information when needed.
# Autonomous bots are preferred. Ask for all prerequisite on start.
# For example, travel dates, preferences, or API credentials.

# Act as a Solutions architect and expert in APIs to create pipeline for bots
# to achieve the specified goals. Autonomous bots are preferred.

PROMPT_FOR_DIRECTOR = """
Act as a Solutions architect and expert in APIs.
""".strip()


class DirectorLexicon(GeneralLexicon):
    role_model_prompt: str = PROMPT_FOR_DIRECTOR


class DirectorGolem(GeneralGolem):
    lexicon_class = DirectorLexicon
