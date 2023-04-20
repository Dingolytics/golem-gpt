from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ''
    OPENAI_ORG_ID: str = ''
    OPENAI_IMAGE_SIZE = '1024x1024'
    HISTORY_ROOT = './history'

    class Config:
        env_file = '.env'
