from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "NetverseIQ"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-super-secret-key-in-production-32chars"

    DATABASE_URL: str = "postgresql+asyncpg://netverseiq:netverseiq_secret@db:5432/netverseiq"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET_KEY: str = "jwt-super-secret-key-change-in-production-min32ch"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    CORS_ORIGINS: str = "http://localhost,http://localhost:80,http://localhost:3000"

    ADMIN_EMAIL: str = "admin@netverseiq.local"
    ADMIN_PASSWORD: str = "Admin@1234"
    ADMIN_NAME: str = "System Admin"

    PLUGINS_DIR: str = "/app/plugins"

    def get_cors_origins(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
