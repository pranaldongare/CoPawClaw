"""
Application configuration — loads from environment variables via pydantic-settings.

Stripped to only the fields needed for the skills platform
(LLM keys, SMTP, GPU endpoints). No MongoDB/auth/document parsing.
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # GPU Server
    MAIN_MODEL: str = "gpt-oss-20b"
    QUERY_URL: str = "http://localhost:11434"
    VISION_URL: str = "http://localhost:11435"
    REMOTE_GPU: bool = False
    LOCAL_BASE_URL: str = "http://localhost"

    # Gemini API Keys (6 for round-robin rotation)
    API_KEY_1: str = ""
    API_KEY_2: str = ""
    API_KEY_3: str = ""
    API_KEY_4: str = ""
    API_KEY_5: str = ""
    API_KEY_6: str = ""

    # OpenAI
    OPENAI_API: str = ""

    # INTERNAL API Configuration
    INTERNAL_BASE_URL: str = ""
    INTERNAL_CLIENT_KEY: str = ""
    INTERNAL_API_TOKEN: str = ""
    INTERNAL_USER_EMAIL: str = ""
    INTERNAL_MODEL_ID: str = ""
    USE_INTERNAL: bool = False

    # SMTP (for email digest)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_USE_TLS: bool = True

    # GitHub (for trending repos)
    GITHUB_TOKEN: str = ""

    # JWT Auth
    SECRET_KEY: str = "changeme"

    # Data directory
    DATA_DIR: str = "./data"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
