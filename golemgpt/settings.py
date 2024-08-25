from enum import IntEnum
from pathlib import Path
from pydantic import BaseSettings


class Verbosity(IntEnum):
    """Output verbosity level."""
    SILENT = 0
    COMPACT = 1
    NORMAL = 2
    VERBOSE = 3
    DEBUG = 4


class Settings(BaseSettings):
    GOLEM_DEBUG: bool = False
    WORKDIR: Path = Path("workdir")
    VERBOSITY_MAIN: Verbosity = Verbosity.NORMAL
    VERBOSITY_CODEX: Verbosity = Verbosity.SILENT

    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"

    BING_SEARCH_API_KEY: str = ""

    class Config:
        env_file = ".env"
