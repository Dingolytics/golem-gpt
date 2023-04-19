from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ''
    OPENAI_ORG_ID: str = ''
    OPENAI_MODEL = 'gpt-3.5-turbo-0301'

    class Config:
        env_file = '.env'