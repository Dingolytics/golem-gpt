from enum import IntEnum
from pathlib import Path
from pydantic import BaseSettings, PyObject


class Verbosity(IntEnum):
    """Output verbosity level."""
    SILENT = 0
    COMPACT = 1
    NORMAL = 2
    VERBOSE = 3
    DEBUG = 4


class Settings(BaseSettings):
    """General Golem-GPT settings."""

    GOLEM_DEBUG: bool = False
    WORKDIR: Path = Path("workdir")
    VERBOSITY_MAIN: Verbosity = Verbosity.NORMAL
    VERBOSITY_CODEX: Verbosity = Verbosity.SILENT

    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    CODEX_CLASS: PyObject = "golemgpt.codex.ReasonableCodex"
    RUNNER_CLASS: PyObject = "golemgpt.runners.JustDoRunner"

    BRAVE_SEARCH_API_KEY: str = ""

    class Config:
        env_file = ".env"
