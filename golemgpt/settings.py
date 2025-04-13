from enum import IntEnum
from pathlib import Path
from pydantic import PyObject
from pydantic_settings import BaseSettings, SettingsConfigDict


class Verbosity(IntEnum):
    """Output verbosity level."""

    SILENT = 0
    COMPACT = 1
    NORMAL = 2
    VERBOSE = 3
    DEBUG = 4


class Settings(BaseSettings):
    """General Golem-GPT settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    GOLEM_DEBUG: bool = False
    WORKDIR: Path = Path("workdir")
    VERBOSITY_MAIN: Verbosity = Verbosity.NORMAL
    VERBOSITY_CODEX: Verbosity = Verbosity.SILENT

    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str = ""
    # OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MODEL: str = "gpt-4o"

    CODEX_CLASS: PyObject = "golemgpt.codex.ReasonableCodex"  # type: ignore
    RUNNER_CLASS: PyObject = "golemgpt.runners.JustDoRunner"  # type: ignore

    BRAVE_SEARCH_API_KEY: str = ""
