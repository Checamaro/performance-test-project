from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@postgres:5432/auth_db"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_auth_topic: str = "auth-events"

    class Config:
        env_file = ".env"


settings = Settings()