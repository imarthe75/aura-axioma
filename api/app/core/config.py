from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:casmarts_secure_pwd@casmarts-core-db-primary:5432/db_core_knowledge"
    REDIS_URL: str = "redis://casmarts-core-cache:6379/2"
    APP_ENV: str = "local"
    
    class Config:
        env_file = ".env"

settings = Settings()
