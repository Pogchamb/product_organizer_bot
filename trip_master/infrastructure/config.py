from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    gemini_api_key: str
    database_url: str = "postgresql+asyncpg://tripmaster:tripmaster@localhost:5432/tripmaster"
    webapp_url: str = "http://localhost:8000"
    host: str = "0.0.0.0"
    port: int = 8000
