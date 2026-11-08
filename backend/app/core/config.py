"""
app/core/config.py
------------------
Application-wide settings loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic Settings model that reads configuration from the environment
    or from a `.env` file located in the working directory."""

    # ------------------------------------------------------------------ #
    #  Database                                                            #
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = "sqlite:///./businesspulse.db"

    # ------------------------------------------------------------------ #
    #  JWT / Security                                                      #
    # ------------------------------------------------------------------ #
    SECRET_KEY: str = "change-this-to-a-random-secret-key-at-least-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ------------------------------------------------------------------ #
    #  CORS / Frontend                                                     #
    # ------------------------------------------------------------------ #
    FRONTEND_URL: str = "http://localhost:5173"

    # ------------------------------------------------------------------ #
    #  Runtime environment                                                 #
    # ------------------------------------------------------------------ #
    ENVIRONMENT: str = "development"

    # ------------------------------------------------------------------ #
    #  Demo credentials (used by seed script)                             #
    # ------------------------------------------------------------------ #
    DEMO_ADMIN_EMAIL: str = "admin@businesspulse.demo"
    DEMO_ADMIN_PASSWORD: str = "Demo@2024!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Singleton instance used throughout the application
settings = Settings()
