
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")

    data_path: str = "data/books.json"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
