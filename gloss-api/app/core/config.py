from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    mock_url: str
    upload_dir: str
    paragraph_timeout: int
    chat_timeout: int

    class Config:
        env_file = ".env"


settings = Settings()
