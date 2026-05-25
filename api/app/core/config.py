from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:casmarts_secure_pwd@casmarts-core-db-primary:5432/db_core_knowledge"
    REDIS_URL: str = "redis://casmarts-core-cache:6379/2"
    APP_ENV: str = "local"

    # Authentik OIDC
    AUTHENTIK_URL: str = "https://auth.casmart.internal"
    AUTHENTIK_CLIENT_ID: str = "axioma"
    AUTHENTIK_INTERNAL_URL: str = "http://casmarts-core-authentik-server:9000"

    class Config:
        env_file = ".env"

settings = Settings()
