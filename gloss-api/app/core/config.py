from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    chat_timeout: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
