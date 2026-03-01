from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Project"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # CORS
    ALLOWED_ORIGINS: str = '["http://localhost:3000"]'

    def get_allowed_origins(self) -> List[str]:
        return json.loads(self.ALLOWED_ORIGINS)

    class Config:
        env_file = ".env"


settings = Settings()
