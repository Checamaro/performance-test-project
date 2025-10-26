import os
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    # В CI используем имена сервисов, локально - localhost
    base_url: str = os.getenv('TEST_BASE_URL', 'http://backend:8000')
    frontend_url: str = os.getenv('FRONTEND_URL', 'http://frontend')
    test_user_email: str = "test_user@example.com"
    test_user_password: str = "testpassword123"

    class Config:
        env_file = ".env.test"


settings = TestSettings()