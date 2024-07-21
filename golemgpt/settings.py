from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    GOLEM_DEBUG: bool = False
    OPENAI_API_KEY: str = ''
    OPENAI_ORG_ID: str = ''
    OPENAI_MODEL: str = ''
    WORKDIR: Path = Path('workdir')

    class Config:
        env_file = '.env'
